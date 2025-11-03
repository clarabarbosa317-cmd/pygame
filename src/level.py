import pygame
from settings import TILE, WIDTH, HEIGHT, COLS, ROWS, NEUTRAL, RED, BLUE, HAZARD, GOAL_R, GOAL_B, BG
from sprites import Tile
from assets import load_tile_textures

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

def load_level(level_path, groups):
    all_tiles   = groups["all_tiles"]
    solids      = groups["solids"]
    color_tiles = groups["color_tiles"]
    hazards     = groups["hazards"]
    doors       = groups["doors"]
    ramps       = groups["ramps"]   # <<< NOVO

    spawns = {"red": None, "blue": None}

    with open(level_path, "r", encoding="utf-8") as f:
        lines = _normalize_lines(f.readlines())

    tex = load_tile_textures()
    grid = [list(line) for line in lines]

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
                t = Tile(x, y, None, deadly=True)
                all_tiles.add(t); hazards.add(t)

            elif ch == "G":
                t = Tile(x, y, None, goal_for="red")
                all_tiles.add(t); doors.add(t)

            elif ch == "H":
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
