# Configurações gerais do jogo
TITULO = "Dino Escape — Tela fixa (tile menor)"

# Janela fixa
WIDTH, HEIGHT = 960, 576
FPS = 60

# Tamanho do bloco (menor que o dino)
TILE = 24                      # era 48
COLS = WIDTH // TILE           # 960/24 = 40
ROWS = HEIGHT // TILE          # 576/24 = 24

# Física / movimento
GRAVITY = 0.8
MOVE_SPEED = 5
JUMP_SPEED = 16

# Tamanho dos dinos (maiores que 1 tile)
PLAYER_H = 48                  # 2x o TILE
PLAYER_W = 48

# Cores
WHITE   = (240, 240, 240)
BLACK   = (15, 15, 20)
RED     = (220, 70, 70)
BLUE    = (70, 120, 220)
NEUTRAL = (125, 125, 125)
HAZARD  = (200, 200, 40)
GOAL_R  = (200, 80, 150)
GOAL_B  = (80, 200, 150)
BG      = (25, 30, 40)
