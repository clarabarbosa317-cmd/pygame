import pygame
from settings import TILE, WIDTH, HEIGHT, COLS, ROWS, NEUTRAL, RED, BLUE, HAZARD, GOAL_R, GOAL_B, BG
from sprites import Tile, AnimatedTile
from assets import load_tile_textures, load_image

# Legenda extra:
# '/' → rampa_sobe  (sobe para a direita)
# '\' → rampa_desce (desce para a direita)
# (demais símbolos iguais: '#', 'R', 'B', 'X', 'G', 'H', '1', '2', '.')

def _normalize_lines(lines):
    lines = [line.rstrip("\n") for line in lines]
    lines = lines[:ROWS]
    lines = [line[:COLS].ljust(COLS, ".") for line in lines]
    while len(lines) < ROWS:
        lines.append("." * COLS)
    return lines

def _is_solid(ch):
    return ch == "#"

def _choose_solid_texture(x, y, grid, tex):
    up    = y > 0            and _is_solid(grid[y-1][x])
    down  = y < ROWS-1       and _is_solid(grid[y+1][x])
    left  = x > 0            and _is_solid(grid[y][x-1])
    right = x < COLS-1       and _is_solid(grid[y][x+1])

    if up and down and left and right:
        key = "fechado"
    elif not up and down and left and right:
        key = "fechado_cima"
    elif up and not down and left and right:
        key = "fechado_embaixo"
    elif up and down and not left and right:
        key = "fechado_esquerda"
    elif up and down and left and not right:
        key = "fechado_direita"
    elif not up and not down and left and right:
        key = "aberto_meio_grama_cima_baixo"
    elif up and down and not left and not right:
        key = "aberto_meio_grama_lados"
    else:
        key = "chao_pedra"

    return tex.get(key, tex["fechado"])

def _slice_portal_spritesheet(sheet):
    """Fatia spritesheet horizontal de 8 frames quadrados"""
    frame_h = sheet.get_height()
    frame_w = frame_h  # frames quadrados
    n = 8  # 8 frames de animação
    
    # Portais são 3x maiores que um TILE (72x72 pixels)
    portal_size = TILE * 3
    
    frames = []
    for i in range(n):
        rect = pygame.Rect(i * frame_w, 0, frame_w, frame_h)
        frame = sheet.subsurface(rect).copy()
        # Redimensiona para 3x o tamanho do TILE
        frame = pygame.transform.scale(frame, (portal_size, portal_size))
        frames.append(frame)
    return frames

def load_portal_sprites():
    """Carrega e fatia os spritesheets dos portais"""
    try:
        portal_red_sheet = load_image("portal_vermelho.png")
        portal_red_frames = _slice_portal_spritesheet(portal_red_sheet)
    except:
        print("Aviso: portal_vermelho.png não encontrado, usando bloco colorido")
        portal_red_frames = None

    try:
        portal_blue_sheet = load_image("portal_azul.png")
        portal_blue_frames = _slice_portal_spritesheet(portal_blue_sheet)
    except:
        print("Aviso: portal_azul.png não encontrado, usando bloco colorido")
        portal_blue_frames = None
    
    return portal_red_frames, portal_blue_frames

def load_level(level_path, groups):
    all_tiles   = groups["all_tiles"]
    solids      = groups["solids"]
    color_tiles = groups["color_tiles"]
    hazards     = groups["hazards"]
    doors       = groups["doors"]
    ramps       = groups["ramps"]

    spawns = {"red": None, "blue": None}

    with open(level_path, "r", encoding="utf-8") as f:
        lines = _normalize_lines(f.readlines())

    tex = load_tile_textures()
    grid = [list(line) for line in lines]

    # Carrega frames dos portais animados
    portal_red_frames, portal_blue_frames = load_portal_sprites()

    for j, line in enumerate(lines):
        for i, ch in enumerate(line):
            x = i * TILE
            y = j * TILE

            if ch == "#":
                image = _choose_solid_texture(i, j, grid, tex)
                t = Tile(x, y, image, solid=True)
                all_tiles.add(t); solids.add(t)

            elif ch == "/":   # rampa sobe (para a direita)
                t = Tile(x, y, tex["rampa_sobe"], slope="up")
                all_tiles.add(t); ramps.add(t)

            elif ch == "\\":  # rampa desce (para a direita)
                t = Tile(x, y, tex["rampa_desce"], slope="down")
                all_tiles.add(t); ramps.add(t)

            elif ch == "R":
                t = Tile(x, y, None, color_kind="red")
                all_tiles.add(t); color_tiles.add(t)

            elif ch == "B":
                t = Tile(x, y, None, color_kind="blue")
                all_tiles.add(t); color_tiles.add(t)

            elif ch == "X":
                t = Tile(x, y, tex["espinho"], deadly=True)
                all_tiles.add(t); hazards.add(t)

            elif ch == "G":  # Portal vermelho (animado)
                if portal_red_frames:
                    t = AnimatedTile(x, y, portal_red_frames, goal_for="red")
                else:
                    t = Tile(x, y, None, goal_for="red")
                all_tiles.add(t); doors.add(t)

            elif ch == "H":  # Portal azul (animado)
                if portal_blue_frames:
                    t = AnimatedTile(x, y, portal_blue_frames, goal_for="blue")
                else:
                    t = Tile(x, y, None, goal_for="blue")
                all_tiles.add(t); doors.add(t)

            elif ch == "1":
                spawns["red"]  = (x + TILE // 2, y + TILE)
            elif ch == "2":
                spawns["blue"] = (x + TILE // 2, y + TILE)

    if spawns["red"]  is None: spawns["red"]  = (TILE*2 + TILE//2, TILE*2)
    if spawns["blue"] is None: spawns["blue"] = (TILE*4 + TILE//2, TILE*2)
    return spawns

def build_level_surface(all_tiles):
    surf = pygame.Surface((WIDTH, HEIGHT))
    surf.fill(BG)
    all_tiles.draw(surf)
    return surf