import pygame
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

# ----------------- Sons (stub) -----------------
def load_sounds():
    return {}
