import pygame
import math
import random
from settings import WIDTH, HEIGHT, FPS, BG
from assets import load_player_sprites, load_image

class MenuButton:
    def __init__(self, x, y, width, height, text, color, hover_color, icon=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False
        self.icon = icon
        self.hover_scale = 1.0
        self.target_scale = 1.0
        
    def update(self, dt):
        """Animação suave ao passar o mouse"""
        self.target_scale = 1.05 if self.is_hovered else 1.0
        self.hover_scale += (self.target_scale - self.hover_scale) * 10 * dt
        
    def draw(self, screen, font):
        # Calcular retângulo escalado
        scale = self.hover_scale
        scaled_w = int(self.rect.width * scale)
        scaled_h = int(self.rect.height * scale)
        scaled_rect = pygame.Rect(0, 0, scaled_w, scaled_h)
        scaled_rect.center = self.rect.center
        
        color = self.hover_color if self.is_hovered else self.color
        
        # Sombra do botão (mais pronunciada quando hover)
        shadow_offset = 6 if self.is_hovered else 4
        shadow_rect = scaled_rect.copy()
        shadow_rect.x += shadow_offset
        shadow_rect.y += shadow_offset
        shadow_surf = pygame.Surface((shadow_rect.width, shadow_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surf, (0, 0, 0, 120), (0, 0, shadow_rect.width, shadow_rect.height), border_radius=12)
        screen.blit(shadow_surf, shadow_rect)
        
        # Botão principal
        pygame.draw.rect(screen, color, scaled_rect, border_radius=12)
        
        # Highlight no topo (efeito de brilho)
        highlight_rect = pygame.Rect(scaled_rect.x + 5, scaled_rect.y + 5, scaled_rect.width - 10, scaled_rect.height // 3)
        highlight_surf = pygame.Surface((highlight_rect.width, highlight_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(highlight_surf, (255, 255, 255, 40), (0, 0, highlight_rect.width, highlight_rect.height), border_radius=8)
        screen.blit(highlight_surf, highlight_rect)
        
        # Borda brilhante
        border_color = (255, 255, 255) if self.is_hovered else (200, 200, 200)
        border_width = 4 if self.is_hovered else 3
        pygame.draw.rect(screen, border_color, scaled_rect, border_width, border_radius=12)
        
        # Ícone (se houver) - usando fonte maior para ícone
        if self.icon:
            icon_font = pygame.font.Font(None, 56)
            icon_surf = icon_font.render(self.icon, True, (255, 255, 255))
            icon_rect = icon_surf.get_rect(midleft=(scaled_rect.left + 30, scaled_rect.centery))
            screen.blit(icon_surf, icon_rect)
        
        # Texto
        text_surf = font.render(self.text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=scaled_rect.center)
        if self.icon:
            text_rect.x += 15  # Offset if there's an icon
        screen.blit(text_surf, text_rect)
        
    def check_hover(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        return self.is_hovered
        
    def check_click(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)

class AnimatedDino:
    def __init__(self, x, y, frames, scale=3.0):
        self.x = x
        self.y = y
        self.frames = [pygame.transform.scale(f, (int(f.get_width() * scale), int(f.get_height() * scale))) for f in frames]
        self.anim_index = 0.0
        self.anim_speed = 12.0
        
    def update(self, dt):
        self.anim_index = (self.anim_index + self.anim_speed * dt) % len(self.frames)
            
    def draw(self, screen):
        frame = self.frames[int(self.anim_index)]
        rect = frame.get_rect(center=(int(self.x), int(self.y)))
        screen.blit(frame, rect)

class Menu:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("DinoWars - Menu")
        self.clock = pygame.time.Clock()
        
        # Carrega imagem de fundo
        self.background = load_image("Preview_2.jpg")
        self.background = pygame.transform.scale(self.background, (WIDTH, HEIGHT))
        
        # Carrega sprites dos dinossauros
        player_frames = load_player_sprites()
        
        # Cria dinossauros animados maiores e em posições fixas
        self.dino_red = AnimatedDino(200, HEIGHT - 200, player_frames["red"], scale=3.0)
        self.dino_blue = AnimatedDino(WIDTH - 200, HEIGHT - 200, player_frames["blue"], scale=3.0)
        
        # Fontes
        self.title_font = pygame.font.Font(None, 120)
        self.button_font = pygame.font.Font(None, 48)
        self.subtitle_font = pygame.font.Font(None, 36)
        
        # Botões (mais largos e com ícones)
        button_width = 300
        button_height = 75
        button_x = WIDTH // 2 - button_width // 2
        
        self.btn_start = MenuButton(
            button_x, HEIGHT // 2 + 20, 
            button_width, button_height,
            "JOGAR", (70, 180, 70), (90, 220, 90), ">"
        )
        
        self.btn_tutorial = MenuButton(
            button_x, HEIGHT // 2 + 110,
            button_width, button_height,
            "TUTORIAL", (70, 120, 220), (90, 150, 255), "?"
        )
        
        self.btn_quit = MenuButton(
            button_x, HEIGHT // 2 + 200,
            button_width, button_height,
            "SAIR", (180, 70, 70), (220, 90, 90), "X"
        )
        
        self.running = True
        self.start_game = False
        self.show_tutorial = False
        
        # Efeito de estrelas no fundo
        self.stars = []
        for i in range(50):
            self.stars.append({
                'x': float(random.randint(0, WIDTH)),
                'y': float(random.randint(0, HEIGHT)),
                'speed': 10 + (i % 20),
                'size': 1 + (i % 3)
            })
    
    def draw_title(self):
        # Título com efeito de sombra
        title_text = "DinoWars"
        
        # Sombra
        shadow = self.title_font.render(title_text, True, (0, 0, 0))
        shadow_rect = shadow.get_rect(center=(WIDTH // 2 + 5, 120 + 5))
        self.screen.blit(shadow, shadow_rect)
        
        # Título principal em amarelo claro
        title = self.title_font.render(title_text, True, (255, 255, 150))
        title_rect = title.get_rect(center=(WIDTH // 2, 120))
        self.screen.blit(title, title_rect)
        
        # Subtítulo em preto
        subtitle = self.subtitle_font.render("Chegue ao portal mágico!", True, (0, 0, 0))
        subtitle_rect = subtitle.get_rect(center=(WIDTH // 2, 200))
        self.screen.blit(subtitle, subtitle_rect)

    def update_stars(self, dt):
        for star in self.stars:
            star['x'] += star['speed'] * dt
            if star['x'] > WIDTH:
                star['x'] = 0
                star['y'] = float(random.randint(0, HEIGHT))
    
    def draw_stars(self):
        for star in self.stars:
            pygame.draw.circle(self.screen, (200, 200, 220), 
                             (int(star['x']), int(star['y'])), 
                             star['size'])
    
    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            mouse_pos = pygame.mouse.get_pos()
            
            # Eventos
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.btn_start.check_click(mouse_pos):
                        self.start_game = True
                        self.running = False
                    elif self.btn_tutorial.check_click(mouse_pos):
                        self.show_tutorial = True
                        self.running = False
                    elif self.btn_quit.check_click(mouse_pos):
                        self.running = False
                        
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        self.start_game = True
                        self.running = False
                    elif event.key == pygame.K_t:
                        self.show_tutorial = True
                        self.running = False
                    elif event.key == pygame.K_ESCAPE:
                        self.running = False
            
            # Atualiza
            self.update_stars(dt)
            self.dino_red.update(dt)
            self.dino_blue.update(dt)
            
            # Verifica hover nos botões
            self.btn_start.check_hover(mouse_pos)
            self.btn_tutorial.check_hover(mouse_pos)
            self.btn_quit.check_hover(mouse_pos)
            
            # Atualiza animações dos botões
            self.btn_start.update(dt)
            self.btn_tutorial.update(dt)
            self.btn_quit.update(dt)
            
            # Desenha
            self.screen.blit(self.background, (0, 0))
            self.draw_stars()
            
            # Desenha dinossauros
            self.dino_red.draw(self.screen)
            self.dino_blue.draw(self.screen)
            
            # Desenha UI
            self.draw_title()
            self.btn_start.draw(self.screen, self.button_font)
            self.btn_tutorial.draw(self.screen, self.button_font)
            self.btn_quit.draw(self.screen, self.button_font)
            
            # Dica de teclas
            hint_text = self.subtitle_font.render("ENTER - Jogar | T - Tutorial | ESC - Sair", True, (180, 180, 180))
            hint_rect = hint_text.get_rect(center=(WIDTH // 2, HEIGHT - 40))
            self.screen.blit(hint_text, hint_rect)
            
            pygame.display.flip()
        
        return (self.start_game, self.show_tutorial)

def show_menu():
    """Função principal para mostrar o menu e retornar (start_game, show_tutorial)."""
    menu = Menu()
    result = menu.run()
    return result

if __name__ == "__main__":
    # Teste do menu standalone
    start_game, show_tutorial = show_menu()
    if start_game:
        print("Iniciando jogo...")
    elif show_tutorial:
        print("Mostrando tutorial...")
    else:
        print("Saindo...")
    pygame.quit()