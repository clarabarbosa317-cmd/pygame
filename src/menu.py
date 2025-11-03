import pygame
import math
import random
from settings import WIDTH, HEIGHT, FPS, BG
from assets import load_player_sprites, load_image

class MenuButton:
    def __init__(self, x, y, width, height, text, color, hover_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False
        
    def draw(self, screen, font):
        color = self.hover_color if self.is_hovered else self.color
        # Sombra do botão
        shadow_rect = self.rect.copy()
        shadow_rect.x += 4
        shadow_rect.y += 4
        pygame.draw.rect(screen, (0, 0, 0), shadow_rect, border_radius=10)
        # Botão principal
        pygame.draw.rect(screen, color, self.rect, border_radius=10)
        pygame.draw.rect(screen, (255, 255, 255), self.rect, 3, border_radius=10)
        
        # Texto
        text_surf = font.render(self.text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)
        
    def check_hover(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        return self.is_hovered
        
    def check_click(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)

class AnimatedDino:
    def __init__(self, x, y, frames, speed):
        self.x = x
        self.y = y
        self.frames = frames
        self.speed = speed
        self.anim_index = 0.0
        self.anim_speed = 12.0
        
    def update(self, dt):
        self.x += self.speed * dt * 60  # Normaliza pela taxa de frames
        self.anim_index = (self.anim_index + self.anim_speed * dt) % len(self.frames)
        
        # Loop quando sai da tela - reaparece em altura aleatória
        if self.x > WIDTH + 100:
            self.x = -100
            self.y = random.randint(HEIGHT // 2, HEIGHT - 100)
            
    def draw(self, screen):
        frame = self.frames[int(self.anim_index)]
        rect = frame.get_rect(center=(int(self.x), int(self.y)))
        screen.blit(frame, rect)

class Meteor:
    def __init__(self, x, y, meteor_images, speed):
        self.x = x
        self.y = y
        self.meteor_images = meteor_images
        self.current_frame = 0
        self.speed = speed
        self.anim_speed = 15.0
        self.anim_counter = 0.0
        self.trail_particles = []
        
    def update(self, dt):
        self.x += self.speed * dt * 60
        
        # Animação do meteoro
        self.anim_counter += self.anim_speed * dt
        if self.anim_counter >= 1.0:
            self.anim_counter = 0.0
            self.current_frame = (self.current_frame + 1) % len(self.meteor_images)
        
        # Adiciona partículas de rastro
        if len(self.trail_particles) < 15:
            self.trail_particles.append({
                'x': self.x - 20,
                'y': self.y,
                'alpha': 255,
                'size': 15
            })
        
        # Atualiza partículas
        for p in self.trail_particles[:]:
            p['alpha'] -= 10
            p['size'] -= 0.8
            if p['alpha'] <= 0:
                self.trail_particles.remove(p)
        
        # Loop - reaparece em altura aleatória
        if self.x > WIDTH + 100:
            self.x = -100
            self.y = random.randint(HEIGHT // 2, HEIGHT - 100)
            
    def draw(self, screen):
        # Desenha rastro de fogo
        for p in self.trail_particles:
            if p['size'] > 0:
                surf = pygame.Surface((int(p['size'] * 2), int(p['size'] * 2)), pygame.SRCALPHA)
                color = (255, int(100 + p['alpha'] * 0.6), 0, int(p['alpha']))
                pygame.draw.circle(surf, color, (int(p['size']), int(p['size'])), int(p['size']))
                screen.blit(surf, (int(p['x'] - p['size']), int(p['y'] - p['size'])))
        
        # Desenha meteoro usando a imagem PNG
        current_img = self.meteor_images[self.current_frame]
        rect = current_img.get_rect(center=(int(self.x), int(self.y)))
        screen.blit(current_img, rect)

class Menu:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("DinoWars - Menu")
        self.clock = pygame.time.Clock()
        
        # Carrega sprites dos dinossauros
        player_frames = load_player_sprites()
        
        # Carrega imagens do meteoro
        meteor_img1 = load_image("meteoro.png")
        meteor_img2 = load_image("meteoro2.png")
        # Redimensiona meteoros para tamanho adequado (60x60)
        meteor_img1 = pygame.transform.scale(meteor_img1, (60, 60))
        meteor_img2 = pygame.transform.scale(meteor_img2, (60, 60))
        self.meteor_images = [meteor_img1, meteor_img2]
        
        # Cria dinossauros animados (velocidade reduzida de 150 para 50)
        start_y1 = random.randint(HEIGHT // 2, HEIGHT - 100)
        start_y2 = random.randint(HEIGHT // 2, HEIGHT - 100)
        self.dino_red = AnimatedDino(100, start_y1, player_frames["red"], 50)
        self.dino_blue = AnimatedDino(250, start_y2, player_frames["blue"], 50)
        
        # Cria meteoro (velocidade reduzida de 180 para 70)
        start_y_meteor = random.randint(HEIGHT // 2, HEIGHT - 100)
        self.meteor = Meteor(-50, start_y_meteor, self.meteor_images, 70)
        
        # Fontes
        self.title_font = pygame.font.Font(None, 120)
        self.button_font = pygame.font.Font(None, 48)
        self.subtitle_font = pygame.font.Font(None, 36)
        
        # Botões
        button_width = 250
        button_height = 70
        button_x = WIDTH // 2 - button_width // 2
        
        self.btn_start = MenuButton(
            button_x, HEIGHT // 2 + 50, 
            button_width, button_height,
            "INICIAR", (70, 180, 70), (90, 220, 90)
        )
        
        self.btn_quit = MenuButton(
            button_x, HEIGHT // 2 + 150,
            button_width, button_height,
            "SAIR", (180, 70, 70), (220, 90, 90)
        )
        
        self.running = True
        self.start_game = False
        
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
        
        # Título principal com gradiente (simulado com múltiplas camadas)
        title = self.title_font.render(title_text, True, (255, 200, 50))
        title_rect = title.get_rect(center=(WIDTH // 2, 120))
        self.screen.blit(title, title_rect)
        
        # Subtítulo
        subtitle = self.subtitle_font.render("Fuja do meteoro!", True, (200, 200, 200))
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
                    elif self.btn_quit.check_click(mouse_pos):
                        self.running = False
                        
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        self.start_game = True
                        self.running = False
                    elif event.key == pygame.K_ESCAPE:
                        self.running = False
            
            # Atualiza
            self.update_stars(dt)
            self.dino_red.update(dt)
            self.dino_blue.update(dt)
            self.meteor.update(dt)
            
            # Verifica hover nos botões
            self.btn_start.check_hover(mouse_pos)
            self.btn_quit.check_hover(mouse_pos)
            
            # Desenha
            self.screen.fill(BG)
            self.draw_stars()
            
            # Desenha elementos animados
            self.meteor.draw(self.screen)
            self.dino_red.draw(self.screen)
            self.dino_blue.draw(self.screen)
            
            # Desenha UI
            self.draw_title()
            self.btn_start.draw(self.screen, self.button_font)
            self.btn_quit.draw(self.screen, self.button_font)
            
            # Instruções
            hint = self.subtitle_font.render("Pressione ENTER ou ESPAÇO para iniciar", True, (150, 150, 150))
            hint_rect = hint.get_rect(center=(WIDTH // 2, HEIGHT - 40))
            self.screen.blit(hint, hint_rect)
            
            pygame.display.flip()
        
        return self.start_game

def show_menu():
    """Função principal para mostrar o menu e retornar se deve iniciar o jogo."""
    menu = Menu()
    should_start = menu.run()
    return should_start

if __name__ == "__main__":
    # Teste do menu standalone
    if show_menu():
        print("Iniciando jogo...")
    else:
        print("Saindo...")
    pygame.quit()
