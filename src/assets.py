import pygame
from os import path
from settings import PLAYER_H, TILE

def _asset_path(*parts):
    here = path.dirname(__file__)
    return path.abspath(path.join(here, "..", "assets", *parts))

def load_image(name):
    surf = pygame.image.load(_asset_path("img", name)).convert_alpha()
    return surf

def _slice_spritesheet(sheet):
    frame_h = sheet.get_height()
    frame_w = frame_h
    n = sheet.get_width() // frame_w

    # fator inteiro para os dinos (ex.: 48/24=2)
    factor = max(1, round(PLAYER_H / frame_h))
    target_w = frame_w * factor
    target_h = frame_h * factor

    frames = []
    for i in range(n):
        rect = pygame.Rect(i * frame_w, 0, frame_w, frame_h)
        frame = sheet.subsurface(rect).copy()
        frame = pygame.transform.scale(frame, (target_w, target_h))  # nearest
        frames.append(frame)
    return frames

def load_player_sprites():
    red_sheet  = load_image("dino_vermelho.png")
    blue_sheet = load_image("dino_azul.png")
    return {"red": _slice_spritesheet(red_sheet),
            "blue": _slice_spritesheet(blue_sheet)}

def _scale_to_tile(img):
    # Ajusta qualquer png 32x32 para o TILE atual (24) sem blur (nearest)
    return pygame.transform.scale(img, (TILE, TILE))

def load_tile_textures():
    """
    Retorna um dict com todas as variantes de blocos sólidos.
    Chaves (nomes autoexplicativos pelos arquivos que você enviou):
      fechado, fechado_cima, fechado_embaixo, fechado_esquerda, fechado_direita,
      aberto_meio_grama_cima_baixo, aberto_meio_grama_lados,
      chao_pedra, rampa_sobe, rampa_desce
    """
def load_tile_textures():
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
        "espinho.png",                     # <<< NOVO
    ]
    tex = {}
    for fname in names:
        key = fname.replace(".png", "")
        tex[key] = _scale_to_tile(load_image(fname))  # escala para TILE (nearest)
    return tex

def load_sounds():
    return {}
