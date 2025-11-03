import pygame
from os import path

from settings import TITULO, WIDTH, HEIGHT, FPS, TILE, BG, RED, BLUE, NEUTRAL
from assets import load_player_sprites, load_sounds, load_tile_textures
from sprites import Player
from level import load_level, build_level_surface


class MenuDino:
    """Dinossauro animado para o menu"""
    def __init__(self, x, y, frames, direction):
        self.x = x
        self.y = y
        self.frames_right = frames
        self.frames_left = [pygame.transform.flip(f, True, False) for f in frames]
        self.direction = direction  # 1 = direita, -1 = esquerda
        self.speed = 2
        self.anim_index = 0.0
        self.anim_speed = 0.15
        
        self.image = self.frames_right[0] if direction == 1 else self.frames_left[0]
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        
    def move(self):
        self.x += self.speed * self.direction
        
        # Inverter direção nas bordas
        if self.x <= 0 or self.x >= WIDTH - self.width:
            self.direction *= -1
        
        # Animar
        frames = self.frames_right if self.direction == 1 else self.frames_left
        self.anim_index = (self.anim_index + self.anim_speed) % len(frames)
        self.image = frames[int(self.anim_index)]
    
    def draw(self, surface):
        surface.blit(self.image, (int(self.x), int(self.y)))


def draw_title(screen):
    """Desenha o título DinoWars"""
    font_title = pygame.font.Font(None, 100)
    title = font_title.render("DinoWars", True, RED)
    title_rect = title.get_rect(center=(WIDTH // 2, 120))
    
    # Sombra
    shadow = font_title.render("DinoWars", True, (0, 0, 0))
    shadow_rect = shadow.get_rect(center=(WIDTH // 2 + 4, 124))
    
    screen.blit(shadow, shadow_rect)
    screen.blit(title, title_rect)


def draw_button(screen, text, x, y, width, height, inactive_color, active_color, mouse_pos):
    """Desenha um botão interativo"""
    button_rect = pygame.Rect(x, y, width, height)
    
    # Cor muda ao passar o mouse
    if button_rect.collidepoint(mouse_pos):
        pygame.draw.rect(screen, active_color, button_rect, border_radius=10)
    else:
        pygame.draw.rect(screen, inactive_color, button_rect, border_radius=10)
    
    # Borda
    pygame.draw.rect(screen, (0, 0, 0), button_rect, 3, border_radius=10)
    
    # Texto
    font = pygame.font.Font(None, 50)
    text_surf = font.render(text, True, (255, 255, 255))
    text_rect = text_surf.get_rect(center=button_rect.center)
    screen.blit(text_surf, text_rect)
    
    return button_rect


def menu_screen(screen, clock, player_frames, tile_textures):
    """Tela de menu com dinossauros animados"""
    
    # Criar dinossauros do menu
    dino_red = MenuDino(150, 290, player_frames["red"], 1)
    dino_blue = MenuDino(700, 390, player_frames["blue"], -1)
    
    # Criar plataformas decorativas usando as texturas reais
    platforms = []
    # Plataforma 1 (para o dino vermelho)
    for i in range(10):
        x = 100 + i * TILE
        y = 320
        img = tile_textures.get("fechado", None)
        platforms.append((img, x, y))
    
    # Plataforma 2 (para o dino azul)
    for i in range(12):
        x = 300 + i * TILE
        y = 420
        img = tile_textures.get("fechado", None)
        platforms.append((img, x, y))
    
    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False  # Sair do jogo
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                button_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT - 130, 200, 60)
                if button_rect.collidepoint(mouse_pos):
                    return True  # Iniciar o jogo
        
        # Fundo
        screen.fill(BG)
        
        # Título
        draw_title(screen)
        
        # Desenhar plataformas
        for img, x, y in platforms:
            if img:
                screen.blit(img, (x, y))
            else:
                # Fallback
                pygame.draw.rect(screen, NEUTRAL, (x, y, TILE, TILE))
        
        # Atualizar e desenhar dinossauros
        dino_red.move()
        dino_blue.move()
        dino_red.draw(screen)
        dino_blue.draw(screen)
        
        # Botão iniciar
        draw_button(screen, "INICIAR", WIDTH // 2 - 100, HEIGHT - 130, 200, 60,
                   (50, 150, 50), (70, 200, 70), mouse_pos)
        
        # Instruções
        font_small = pygame.font.Font(None, 30)
        text1 = font_small.render("Vermelho: A/D mover, W pular", True, RED)
        text2 = font_small.render("Azul: Setas mover, Seta cima pular", True, BLUE)
        screen.blit(text1, (WIDTH // 2 - 180, HEIGHT - 80))
        screen.blit(text2, (WIDTH // 2 - 200, HEIGHT - 50))
        
        pygame.display.flip()
        clock.tick(FPS)
    
    return False


class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(TITULO)
        self.clock = pygame.time.Clock()

        # Carregar recursos
        self.player_frames = load_player_sprites()
        self.tile_textures = load_tile_textures()
        self.sounds = load_sounds()
        
        self.running = True
        self.in_menu = True
        
    def load_game_level(self):
        """Carrega o nível do jogo"""
        # Grupos
        self.all_tiles = pygame.sprite.Group()
        self.solids = pygame.sprite.Group()
        self.color_tiles = pygame.sprite.Group()
        self.hazards = pygame.sprite.Group()
        self.doors = pygame.sprite.Group()
        self.ramps = pygame.sprite.Group()

        # Carregar nível
        level_path = path.abspath(path.join(path.dirname(__file__), "..", "levels", "level1.txt"))
        spawns = load_level(level_path, {
            "all_tiles": self.all_tiles,
            "solids": self.solids,
            "color_tiles": self.color_tiles,
            "hazards": self.hazards,
            "doors": self.doors,
            "ramps": self.ramps,
        })

        self.level_surface = build_level_surface(self.all_tiles)

        # Criar jogadores
        self.p1 = Player(spawns["red"][0], spawns["red"][1], "red", self.player_frames["red"])
        self.p2 = Player(spawns["blue"][0], spawns["blue"][1], "blue", self.player_frames["blue"])
        self.players = pygame.sprite.Group(self.p1, self.p2)

    def check_level_complete(self):
        return self.p1.in_goal and self.p2.in_goal

    def reset_level(self):
        for p in (self.p1, self.p2):
            p._respawn()

    def game_loop(self):
        """Loop principal do jogo"""
        while self.running and not self.in_menu:
            dt = self.clock.tick(FPS) / 1000.0
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return
                
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        self.reset_level()
                    elif event.key == pygame.K_ESCAPE:
                        self.in_menu = True  # Voltar ao menu
                        return

            keys = pygame.key.get_pressed()

            # Atualizar jogadores
            self.p1.update(keys, self.solids, self.color_tiles, self.hazards, 
                          self.doors, self.ramps, (pygame.K_a, pygame.K_d, pygame.K_w), dt)
            self.p2.update(keys, self.solids, self.color_tiles, self.hazards, 
                          self.doors, self.ramps, (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP), dt)

            # Verificar conclusão do nível
            if self.check_level_complete():
                font = pygame.font.Font(None, 74)
                victory_text = font.render("NIVEL COMPLETO!", True, (255, 215, 0))
                # Você pode adicionar lógica para próximo nível aqui
                self.reset_level()

            # Desenhar
            self.screen.blit(self.level_surface, (0, 0))
            self.players.draw(self.screen)
            
            # UI do jogo
            font_small = pygame.font.Font(None, 25)
            text = font_small.render("ESC: Menu | R: Reiniciar", True, (255, 255, 255))
            self.screen.blit(text, (10, 10))
            
            # Mostrar status dos objetivos
            if self.p1.in_goal or self.p2.in_goal:
                status_text = font_small.render("Aguardando o outro jogador...", True, (255, 215, 0))
                self.screen.blit(status_text, (WIDTH // 2 - 150, HEIGHT - 30))
            
            pygame.display.flip()

    def run(self):
        """Loop principal do programa"""
        while self.running:
            if self.in_menu:
                # Mostrar menu
                start_game = menu_screen(self.screen, self.clock, 
                                        self.player_frames, self.tile_textures)
                
                if not start_game:
                    self.running = False  # Usuário fechou a janela
                else:
                    # Iniciar jogo
                    self.in_menu = False
                    self.load_game_level()
            else:
                # Rodar jogo
                self.game_loop()
        
        pygame.quit()


if __name__ == "__main__":
    Game().run()