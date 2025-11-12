import pygame
from settings import TILE, WIDTH, HEIGHT, COLS, ROWS, NEUTRAL, RED, BLUE, HAZARD, GOAL_R, GOAL_B, BG
from sprites import Tile, AnimatedTile, PatrolEnemy, FallingEnemy, VerticalPatrolEnemy
from assets import load_tile_textures, load_image

# Legenda dos níveis:
# '.' = vazio
# '#' = bloco sólido
# 'X' = spike (mata)
# '/' = rampa sobe (para direita)
# '\' = rampa desce (para direita)
# 'R' = tile vermelho (só dino vermelho pode pisar)
# 'B' = tile azul (só dino azul pode pisar)
# 'G' = portal VERMELHO (goal para dino vermelho)
# 'H' = portal AZUL (goal para dino azul)
# '1' = spawn do dino vermelho
# '2' = spawn do dino azul
# 'M' = meteoro patrulheiro horizontal
# 'F' = meteoro que cai do teto
# 'V' = patrulha vertical (voa)

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
        frame = sheet.subsurface(pygame.Rect(i * frame_w, 0, frame_w, frame_h)).copy()
        frame = pygame.transform.scale(frame, (portal_size, portal_size))
        frames.append(frame)
    return frames

def _load_portal_frames():
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

    try:
        with open(level_path, "r", encoding="utf-8") as f:
            lines = _normalize_lines(f.readlines())
    except FileNotFoundError:
        print(f"ERRO: Arquivo de nível não encontrado: {level_path}")
        # Cria um nível vazio de emergência
        lines = ["." * COLS for _ in range(ROWS)]
        # Adiciona chão
        lines[-1] = "#" * COLS
        # Adiciona spawns
        lines[-2] = list(lines[-2])
        lines[-2][5] = "1"
        lines[-2][10] = "2"
        lines[-2] = "".join(lines[-2])

    tex = load_tile_textures()
    portal_red_frames, portal_blue_frames = _load_portal_frames()

    grid = lines

    for j, row in enumerate(grid):
        for i, ch in enumerate(row):
            x = i * TILE
            y = j * TILE

            if ch == "#":
                image = _choose_solid_texture(i, j, grid, tex)
                t = Tile(x, y, image, solid=True)
                groups["all_tiles"].add(t)
                groups["solids"].add(t)

            elif ch == "R":
                image = tex.get("tile_vermelho") if "tile_vermelho" in tex else None
                t = Tile(x, y, image, solid=True, color_kind="red")
                groups["all_tiles"].add(t)
                groups["color_tiles"].add(t)

            elif ch == "B":
                image = tex.get("tile_azul") if "tile_azul" in tex else None
                t = Tile(x, y, image, solid=True, color_kind="blue")
                groups["all_tiles"].add(t)
                groups["color_tiles"].add(t)

            elif ch == "X":
                image = tex.get("espinho", None)
                t = Tile(x, y, image, deadly=True)
                groups["all_tiles"].add(t)
                groups["hazards"].add(t)

            elif ch == "/":
                image = tex.get("rampa_sobe", None)
                t = Tile(x, y, image, solid=True, slope="up")
                groups["all_tiles"].add(t)
                groups["ramps"].add(t)

            elif ch == "\\":
                image = tex.get("rampa_desce", None)
                t = Tile(x, y, image, solid=True, slope="down")
                groups["all_tiles"].add(t)
                groups["ramps"].add(t)

            elif ch == "G":
                if portal_red_frames:
                    t = AnimatedTile(x - (TILE), y - (TILE*2), portal_red_frames, goal_for="red")
                else:
                    t = Tile(x, y, None, goal_for="red")
                groups["all_tiles"].add(t)
                groups["doors"].add(t)

            elif ch == "H":
                if portal_blue_frames:
                    t = AnimatedTile(x - (TILE), y - (TILE*2), portal_blue_frames, goal_for="blue")
                else:
                    t = Tile(x, y, None, goal_for="blue")
                groups["all_tiles"].add(t)
                groups["doors"].add(t)

            elif ch == "1":
                spawns["red"]  = (x + TILE // 2, y + TILE)
            elif ch == "2":
                spawns["blue"] = (x + TILE // 2, y + TILE)
            
            # Inimigos
            elif ch == "M":
                # Meteoro patrulheiro horizontal
                try:
                    meteor_img = load_image("meteoro.png")
                    meteor_img = pygame.transform.scale(meteor_img, (TILE, TILE))
                    enemy = PatrolEnemy(x, y, meteor_img, patrol_distance=5)
                    if "enemies" in groups:
                        groups["enemies"].add(enemy)
                except Exception:
                    print("Aviso: meteoro.png não encontrado")
            
            elif ch == "F":
                # Meteoro que cai do teto
                try:
                    meteor_img = load_image("meteoro2.png")
                    meteor_img = pygame.transform.scale(meteor_img, (TILE, TILE))
                    enemy = FallingEnemy(x, y, meteor_img, fall_delay=2.0)
                    if "enemies" in groups:
                        groups["enemies"].add(enemy)
                except Exception:
                    print("Aviso: meteoro2.png não encontrado")
            
            elif ch == "V":
                # Patrulha vertical (voa)
                try:
                    meteor_img = load_image("meteoro.png")
                    meteor_img = pygame.transform.scale(meteor_img, (TILE, TILE))
                    meteor_img = pygame.transform.rotate(meteor_img, 45)  # Rotaciona para parecer diferente
                    enemy = VerticalPatrolEnemy(x, y, meteor_img, patrol_distance=4)
                    if "enemies" in groups:
                        groups["enemies"].add(enemy)
                except Exception:
                    print("Aviso: meteoro.png não encontrado para patrulha vertical")

    # Spawns padrão caso não encontre no mapa
    if spawns["red"]  is None: 
        spawns["red"]  = (TILE*2 + TILE//2, HEIGHT - TILE*3)
        print("Aviso: Spawn do dino vermelho (1) não encontrado, usando posição padrão")
    if spawns["blue"] is None: 
        spawns["blue"] = (TILE*4 + TILE//2, HEIGHT - TILE*3)
        print("Aviso: Spawn do dino azul (2) não encontrado, usando posição padrão")
    
    return spawns

def build_level_surface(all_tiles):
    # Camada transparente apenas com os tiles/objetos (sem pintar fundo).
    surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    all_tiles.draw(surf)
    return surf
