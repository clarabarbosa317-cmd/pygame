import pygame
import numpy as np
from os import path
from settings import PLAYER_H, TILE, WIDTH, HEIGHT

# ----------------- Utils -----------------
def _asset_path(*parts):
    here = path.dirname(__file__)
    return path.abspath(path.join(here, "..", "assets", *parts))

def load_image(name):
    """Carrega imagem de assets/img com alpha por pixel."""
    return pygame.image.load(_asset_path("img", name)).convert_alpha()

def _slice_spritesheet(sheet):
    """Fatia uma spritesheet horizontal em frames quadrados."""
    frame_h = sheet.get_height()
    frame_w = frame_h
    n = max(1, sheet.get_width() // frame_w)
    frames = []
    for i in range(n):
        rect = pygame.Rect(i * frame_w, 0, frame_w, frame_h)
        frames.append(sheet.subsurface(rect).copy())
    return frames

def _scale_to_h(frames, target_h):
    out = []
    for f in frames:
        w = int(round(f.get_width() * (target_h / f.get_height())))
        out.append(pygame.transform.scale(f, (w, target_h)))
    return out

def _scale_to_tile(surf):
    return pygame.transform.scale(surf, (TILE, TILE))

# ----------------- Players -----------------
def load_player_sprites():
    """
    Retorna {'red': [frames...], 'blue': [frames...]} dimensionados para PLAYER_H.
    Tenta nomes comuns e faz fallback para um retângulo colorido se não encontrar.
    """
    result = {}

    def _load_try(names, tint=None):
        sheet = None
        for n in names:
            try:
                sheet = load_image(n)
                break
            except Exception:
                continue
        if sheet is None:
            # Fallback simples
            surf = pygame.Surface((PLAYER_H, PLAYER_H), pygame.SRCALPHA)
            surf.fill(tint or (200, 200, 200))
            return [surf]
        frames = _slice_spritesheet(sheet)
        return _scale_to_h(frames, PLAYER_H)

    result["red"]  = _load_try(["dino_vermelho.png", "dino_red.png", "player_red.png"], (220, 70, 70))
    result["blue"] = _load_try(["dino_azul.png", "dino_blue.png", "player_blue.png"], (70, 140, 240))
    return result

# ----------------- Tiles / Textures -----------------
def load_tile_textures():
    """Carrega e escala texturas de tiles para TILE. Chaves combinam com as regras do level."""
    names = [
        "fechado.png",
        "fechado_cima.png",
        "fechado_embaixo.png",
        "fechado_esquerda.png",
        "fechado_direita.png",
        "aberto_meio_grama_cima_baixo.png",
        "aberto_meio_grama_lados.png",
        "chao_pedra.png",
        "rampa_sobe.png",
        "rampa_desce.png",
        "espinho.png",
        "tile_vermelho.png",
        "tile_azul.png",
        "portal_vermelho.png",
        "portal_azul.png",
    ]
    tex = {}
    for fname in names:
        key = fname.replace(".png", "")
        try:
            tex[key] = _scale_to_tile(load_image(fname))
        except Exception:
            s = pygame.Surface((TILE, TILE), pygame.SRCALPHA)
            s.fill((120, 120, 120))
            tex[key] = s
    return tex

# ----------------- Backgrounds -----------------
def load_backgrounds():
    """Carrega fase1..fase6.png e redimensiona para a janela. Retorna {nivel:int -> Surface}."""
    bgs = {}
    for i in range(1, 7):
        fname = f"fase{i}.png"
        try:
            img = load_image(fname)
            scaled = pygame.transform.scale(img, (WIDTH, HEIGHT)).convert_alpha()
            bgs[i] = scaled
        except Exception:
            # Se não existir, simplesmente não adiciona
            continue
    return bgs

# ----------------- Sons -----------------
def _generate_sweep(start_freq, end_freq, duration, volume=0.3, sample_rate=22050):
    """Gera um sweep de frequência (chirp)"""
    n_samples = int(duration * sample_rate)
    t = np.linspace(0, duration, n_samples)
    freq = np.linspace(start_freq, end_freq, n_samples)
    wave = np.sin(2 * np.pi * freq * t)
    envelope = np.ones(n_samples)
    fade_samples = int(0.05 * sample_rate)
    envelope[:fade_samples] = np.linspace(0, 1, fade_samples)
    envelope[-fade_samples:] = np.linspace(1, 0, fade_samples)
    wave = wave * envelope * volume * 32767
    stereo = np.column_stack((wave.astype(np.int16), wave.astype(np.int16)))
    return pygame.sndarray.make_sound(stereo)

def _generate_jump_sound():
    """Som de pulo - sweep ascendente curto"""
    return _generate_sweep(200, 600, 0.15, volume=0.15)

def _generate_land_sound():
    """Som de pousar - thump curto"""
    return _generate_sweep(400, 100, 0.08, volume=0.10)

def _generate_death_sound():
    """Som de morte - sweep descendente"""
    return _generate_sweep(800, 100, 0.4, volume=0.25)

def _generate_collect_sound():
    """Som de coleta - arpejo ascendente"""
    sample_rate = 22050
    duration = 0.3
    n_samples = int(duration * sample_rate)
    frequencies = [523, 659, 784]  # C, E, G
    wave = np.zeros(n_samples)
    
    for i, freq in enumerate(frequencies):
        start = int(i * n_samples / len(frequencies))
        end = int((i + 1) * n_samples / len(frequencies))
        t = np.linspace(0, duration / len(frequencies), end - start)
        note = np.sin(2 * np.pi * freq * t)
        wave[start:end] = note
    
    envelope = np.exp(-3 * np.linspace(0, 1, n_samples))
    wave = wave * envelope * 0.2 * 32767
    stereo = np.column_stack((wave.astype(np.int16), wave.astype(np.int16)))
    return pygame.sndarray.make_sound(stereo)

def _generate_victory_sound():
    """Som de vitória - fanfarra alegre"""
    sample_rate = 22050
    duration = 1.0
    n_samples = int(duration * sample_rate)
    notes = [(523, 0, 0.3), (659, 0.3, 0.6), (784, 0.6, 0.9), (1047, 0.9, 1.0)]
    
    wave = np.zeros(n_samples)
    for freq, start_time, end_time in notes:
        start_idx = int(start_time * sample_rate)
        end_idx = int(end_time * sample_rate)
        t = np.linspace(0, end_time - start_time, end_idx - start_idx)
        note = np.sin(2 * np.pi * freq * t)
        note += 0.3 * np.sin(2 * np.pi * freq * 2 * t)
        wave[start_idx:end_idx] += note
    
    envelope = np.exp(-2 * np.linspace(0, 1, n_samples))
    wave = wave * envelope * 0.35 * 32767
    stereo = np.column_stack((wave.astype(np.int16), wave.astype(np.int16)))
    return pygame.sndarray.make_sound(stereo)

def _generate_defeat_sound():
    """Som de derrota - sweep descendente triste"""
    sample_rate = 22050
    duration = 1.5
    n_samples = int(duration * sample_rate)
    notes = [(392, 0, 0.3), (349, 0.3, 0.6), (330, 0.6, 0.9), (294, 0.9, 1.2), (262, 1.2, 1.5)]
    
    wave = np.zeros(n_samples)
    for freq, start_time, end_time in notes:
        start_idx = int(start_time * sample_rate)
        end_idx = int(end_time * sample_rate)
        t = np.linspace(0, end_time - start_time, end_idx - start_idx)
        note = np.sin(2 * np.pi * freq * t)
        wave[start_idx:end_idx] += note
    
    envelope = np.exp(-1.5 * np.linspace(0, 1, n_samples))
    wave = wave * envelope * 0.3 * 32767
    stereo = np.column_stack((wave.astype(np.int16), wave.astype(np.int16)))
    return pygame.sndarray.make_sound(stereo)

def _generate_ambient_music(level_number):
    """Gera música ambiente baseada no nível"""
    sample_rate = 22050
    duration = 4.0
    n_samples = int(duration * sample_rate)
    
    # Escolhe progressão baseada no nível
    if level_number <= 2:
        chord_progression = [
            [(220, 262, 330), 0, 1],  # Am
            [(175, 220, 262), 1, 2],  # F
            [(131, 165, 196), 2, 3],  # C
            [(196, 247, 294), 3, 4],  # G
        ]
    elif level_number <= 4:
        chord_progression = [
            [(262, 330, 392), 0, 1],  # C
            [(196, 247, 294), 1, 2],  # G
            [(220, 262, 330), 2, 3],  # Am
            [(175, 220, 262), 3, 4],  # F
        ]
    else:
        chord_progression = [
            [(147, 175, 220), 0, 1],  # Dm
            [(117, 147, 175), 1, 2],  # Bb
            [(98, 117, 147), 2, 3],   # Gm
            [(110, 139, 165), 3, 4],  # A
        ]
    
    wave = np.zeros(n_samples)
    
    for chord, start_time, end_time in chord_progression:
        start_idx = int(start_time * sample_rate)
        end_idx = int(end_time * sample_rate)
        t = np.linspace(0, end_time - start_time, end_idx - start_idx)
        
        chord_wave = np.zeros(end_idx - start_idx)
        for freq in chord:
            chord_wave += np.sin(2 * np.pi * freq * t)
        
        local_envelope = np.ones(end_idx - start_idx)
        fade = int(0.1 * sample_rate)
        local_envelope[:fade] = np.linspace(0, 1, fade)
        local_envelope[-fade:] = np.linspace(1, 0, fade)
        
        wave[start_idx:end_idx] += chord_wave * local_envelope
    
    wave = wave / np.max(np.abs(wave))
    wave = wave * 0.15 * 32767
    stereo = np.column_stack((wave.astype(np.int16), wave.astype(np.int16)))
    return pygame.sndarray.make_sound(stereo)

def load_sounds():
    """Carrega/gera todos os sons do jogo"""
    try:
        sounds = {
            'jump': _generate_jump_sound(),
            'land': _generate_land_sound(),
            'death': _generate_death_sound(),
            'collect': _generate_collect_sound(),
            'victory': _generate_victory_sound(),
            'defeat': _generate_defeat_sound(),
        }
        
        # Música ambiente por nível
        sounds['music'] = {}
        for level in range(1, 7):
            sounds['music'][level] = _generate_ambient_music(level)
        
        print("✓ Sons carregados com sucesso!")
        return sounds
    except Exception as e:
        print(f"Aviso: Não foi possível carregar sons: {e}")
        return {}
