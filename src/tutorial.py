import pygame
import math
from settings import WIDTH, HEIGHT, FPS, TILE, RED, BLUE
from assets import load_player_sprites, load_tile_textures, load_image

class TutorialScreen:
    def __init__(self):
        self.screen = pygame.display.get_surface()
        self.clock = pygame.time.Clock()
        
        self.title_font = pygame.font.Font(None, 72)
        self.heading_font = pygame.font.Font(None, 48)
        self.text_font = pygame.font.Font(None, 32)
        self.small_font = pygame.font.Font(None, 24)
        
        self.player_frames = load_player_sprites()
        self.tiles = load_tile_textures()
        
        self.anim_time = 0.0
        self.page = 0
        self.max_pages = 4
        
        self.bg_color = (20, 25, 35)
        self.panel_color = (35, 40, 55)
        self.accent_color = (100, 200, 255)
        self.text_color = (240, 240, 245)
        self.dim_text = (160, 165, 175)
        
        self.running = True
        
    def draw_panel(self, x, y, w, h, alpha=255):
        panel = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.rect(panel, (0, 0, 0, 100), (4, 4, w, h), border_radius=15)
        pygame.draw.rect(panel, (*self.panel_color, alpha), (0, 0, w, h), border_radius=15)
        pygame.draw.rect(panel, (*self.accent_color, alpha), (0, 0, w, h), 3, border_radius=15)
        self.screen.blit(panel, (x, y))
        

    def icon_color_for(self, icon: str, text: str):
        """Escolhe cor do ícone por contexto: Espinho/Perigo -> vermelho; Rampa -> laranja; Portal/Portais -> roxo; Pausar -> amarelo; Reiniciar -> laranja; Cooperacao -> verde; default -> accent."""
        low = (text or '').lower()
        if icon in ('X', '!') or 'espinho' in low or 'perigo' in low:
            return (235, 90, 90)
        if 'rampa' in low:
            return (255, 180, 80)
        if 'portal' in low or 'portais' in low:
            return (160, 120, 255)
        if icon == 'P' or 'pausar' in low:
            return (255, 220, 100)
        if icon == 'R' or 'reiniciar' in low:
            return (255, 150, 80)
        if icon == '&' or 'cooperacao' in low:
            return (100, 255, 150)
        return self.accent_color
    def draw_key(self, x, y, text, size=50):
        key_surf = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.rect(key_surf, (0, 0, 0, 150), (3, 3, size, size), border_radius=8)
        pygame.draw.rect(key_surf, (60, 65, 80), (0, 0, size, size), border_radius=8)
        pygame.draw.rect(key_surf, (120, 130, 150), (0, 0, size, size), 2, border_radius=8)
        pygame.draw.rect(key_surf, (80, 85, 100), (0, 0, size, size-10), border_radius=8)
        
        key_text = self.text_font.render(text, True, (255, 255, 255))
        key_rect = key_text.get_rect(center=(size//2, size//2))
        key_surf.blit(key_text, key_rect)
        
        self.screen.blit(key_surf, (x, y))
        
    def draw_animated_dino(self, x, y, color, scale=2.0):
        frames = self.player_frames[color]
        frame_idx = int((self.anim_time * 8) % len(frames))
        frame = frames[frame_idx]
        
        w, h = frame.get_size()
        scaled = pygame.transform.scale(frame, (int(w * scale), int(h * scale)))
        bounce = math.sin(self.anim_time * 3) * 5
        
        rect = scaled.get_rect(center=(x, y + bounce))
        self.screen.blit(scaled, rect)
        
    def draw_tile_example(self, x, y, tile_type, label=""):
        if tile_type in self.tiles:
            tile = self.tiles[tile_type]
            scaled = pygame.transform.scale(tile, (TILE * 2, TILE * 2))
            self.screen.blit(scaled, (x, y))
        else:
            pygame.draw.rect(self.screen, (100, 100, 100), (x, y, TILE * 2, TILE * 2))
        
        if label:
            text = self.small_font.render(label, True, self.text_color)
            text_rect = text.get_rect(center=(x + TILE, y + TILE * 2 + 20))
            self.screen.blit(text, text_rect)
    
    def draw_page_0_welcome(self):
        # Titulo com efeito de brilho
        title = self.title_font.render("DinoWars", True, (255, 255, 150))
        title_glow = self.title_font.render("DinoWars", True, (255, 200, 100, 100))
        
        glow_offset = math.sin(self.anim_time * 2) * 3
        title_rect = title.get_rect(center=(WIDTH // 2, 80))
        glow_rect = title_glow.get_rect(center=(WIDTH // 2 + glow_offset, 80 + glow_offset))
        
        self.screen.blit(title_glow, glow_rect)
        self.screen.blit(title, title_rect)
        
        panel_w, panel_h = 750, 300
        panel_x = (WIDTH - panel_w) // 2
        panel_y = 160
        self.draw_panel(panel_x, panel_y, panel_w, panel_h)
        
        story_lines = [
            "Bem-vindo ao DinoWars!",
            "",
            "Dois dinossauros estao presos em um mundo",
            "cheio de perigos e desafios.",
            "",
            "Trabalhem juntos para alcancar os portais",
            "magicos e escapar de cada nivel!",
            "",
            "Mas cuidado: cada dino so pode pisar",
            "em plataformas da sua cor!"
        ]
        
        y_offset = panel_y + 30
        for line in story_lines:
            if line == "":
                y_offset += 10
                continue
            
            color = self.text_color if line != story_lines[0] else self.accent_color
            font = self.heading_font if line == story_lines[0] else self.text_font
            
            text = font.render(line, True, color)
            text_rect = text.get_rect(center=(WIDTH // 2, y_offset))
            self.screen.blit(text, text_rect)
            y_offset += 30
        
        self.draw_animated_dino(WIDTH // 4, HEIGHT - 80, "red", 2.5)
        self.draw_animated_dino(WIDTH * 3 // 4, HEIGHT - 80, "blue", 2.5)
        
    def draw_page_1_controls(self):
        title = self.heading_font.render("Controles", True, self.accent_color)
        title_rect = title.get_rect(center=(WIDTH // 2, 60))
        self.screen.blit(title, title_rect)
        
        # Painel jogador 1
        p1_x, p1_y = 70, 130
        p1_w, p1_h = 400, 340
        self.draw_panel(p1_x, p1_y, p1_w, p1_h)
        
        p1_title = self.text_font.render("Jogador 1 (Vermelho)", True, (255, 100, 100))
        p1_title_rect = p1_title.get_rect(center=(p1_x + p1_w//2, p1_y + 25))
        self.screen.blit(p1_title, p1_title_rect)
        
        self.draw_animated_dino(p1_x + p1_w//2, p1_y + 90, "red", 1.8)
        
        key_y = p1_y + 170
        key_spacing = 90
        key_start = p1_x + 50
        self.draw_key(key_start, key_y, "A", 55)
        self.draw_key(key_start + key_spacing, key_y, "D", 55)
        self.draw_key(key_start + key_spacing*2, key_y, "W", 55)
        
        move_text = self.small_font.render("Mover", True, self.dim_text)
        move_rect = move_text.get_rect(center=(key_start + key_spacing//2, key_y + 75))
        self.screen.blit(move_text, move_rect)
        
        jump_text = self.small_font.render("Pular", True, self.dim_text)
        jump_rect = jump_text.get_rect(center=(key_start + key_spacing*2, key_y + 75))
        self.screen.blit(jump_text, jump_rect)
        
        # Painel jogador 2
        p2_x = p1_x + p1_w + 20
        p2_y = p1_y
        p2_w, p2_h = p1_w, p1_h
        self.draw_panel(p2_x, p2_y, p2_w, p2_h)
        
        p2_title = self.text_font.render("Jogador 2 (Azul)", True, (100, 150, 255))
        p2_title_rect = p2_title.get_rect(center=(p2_x + p2_w//2, p2_y + 25))
        self.screen.blit(p2_title, p2_title_rect)
        
        self.draw_animated_dino(p2_x + p2_w//2, p2_y + 90, "blue", 1.8)
        
        key_y = p2_y + 170
        key_start = p2_x + 50
        self.draw_key(key_start, key_y, "<", 55)
        self.draw_key(key_start + key_spacing, key_y, ">", 55)
        self.draw_key(key_start + key_spacing*2, key_y, "^", 55)
        
        move_text = self.small_font.render("Mover", True, self.dim_text)
        move_rect = move_text.get_rect(center=(key_start + key_spacing//2, key_y + 75))
        self.screen.blit(move_text, move_rect)
        
        jump_text = self.small_font.render("Pular", True, self.dim_text)
        jump_rect = jump_text.get_rect(center=(key_start + key_spacing*2, key_y + 75))
        self.screen.blit(jump_text, jump_rect)
        
    def draw_page_2_mechanics(self):
        title = self.heading_font.render("Mecanicas do Jogo", True, self.accent_color)
        title_rect = title.get_rect(center=(WIDTH // 2, 60))
        self.screen.blit(title, title_rect)
        
        panel_y = 120
        panel_w = 800
        self.draw_panel(80, panel_y, panel_w, 160)
        
        tiles_title = self.text_font.render("Tipos de Plataformas:", True, self.text_color)
        self.screen.blit(tiles_title, (110, panel_y + 15))
        
        tile_x = 140
        tile_y = panel_y + 55
        spacing = 140
        
        self.draw_tile_example(tile_x, tile_y, "fechado", "Normal")
        self.draw_tile_example(tile_x + spacing, tile_y, "tile_vermelho", "Vermelho")
        self.draw_tile_example(tile_x + spacing*2, tile_y, "tile_azul", "Azul")
        self.draw_tile_example(tile_x + spacing*3, tile_y, "espinho", "Perigo!")
        self.draw_tile_example(tile_x + spacing*4, tile_y, "rampa_sobe", "Rampa")
        
        rules_y = panel_y + 190
        self.draw_panel(80, rules_y, panel_w, 130)
        
        rules = [
            ("X", "Espinhos matam instantaneamente (voce reaparece)"),
            ("*", "Ambos os jogadores devem chegar aos portais")
        ]
        
        y_offset = rules_y + 30
        for icon, rule_text in rules:
            icon_color = self.icon_color_for(icon, rule_text)
            icon_surf = self.text_font.render(icon, True, icon_color)
            self.screen.blit(icon_surf, (110, y_offset))
            
            text = self.text_font.render(rule_text, True, self.text_color)
            self.screen.blit(text, (150, y_offset))
            y_offset += 48
            
    def draw_page_3_tips(self):
        title = self.heading_font.render("Dicas & Truques", True, self.accent_color)
        title_rect = title.get_rect(center=(WIDTH // 2, 60))
        self.screen.blit(title, title_rect)
        
        panel_x, panel_y = 80, 120
        panel_w, panel_h = 800, 380
        self.draw_panel(panel_x, panel_y, panel_w, panel_h)
        
        tips = [
            ("P", "Pausar", "ESC ou P pausa o jogo"),
            ("R", "Reiniciar", "R reinicia o nivel (no pause)"),
            ("&", "Cooperacao", "Trabalhem juntos para vencer!"),
        ]
        
        y_offset = panel_y + 40
        for icon, tip_title, tip_text in tips:
            icon_color = self.icon_color_for(icon, tip_title + " " + tip_text)
            icon_text = self.heading_font.render(icon, True, icon_color)
            self.screen.blit(icon_text, (panel_x + 30, y_offset - 5))
            
            title_text = self.text_font.render(tip_title, True, self.accent_color)
            self.screen.blit(title_text, (panel_x + 90, y_offset))
            
            desc_text = self.small_font.render(tip_text, True, self.dim_text)
            self.screen.blit(desc_text, (panel_x + 90, y_offset + 32))
            
            y_offset += 70
        
    def draw_page_indicators(self):
        dots_y = HEIGHT - 100
        for i in range(self.max_pages):
            x = WIDTH // 2 - (self.max_pages * 20) // 2 + i * 20
            if i == self.page:
                pygame.draw.circle(self.screen, self.accent_color, (x, dots_y), 8)
                pygame.draw.circle(self.screen, (255, 255, 255), (x, dots_y), 8, 2)
            else:
                pygame.draw.circle(self.screen, (80, 85, 95), (x, dots_y), 6)
                
    def draw_navigation(self):
        nav_y = HEIGHT - 60
        
        if self.page > 0:
            left_text = self.small_font.render("< Anterior (A)", True, self.dim_text)
            self.screen.blit(left_text, (30, nav_y))
        
        if self.page < self.max_pages - 1:
            right_text = self.small_font.render("Proximo (D) >", True, self.dim_text)
            right_rect = right_text.get_rect(right=WIDTH - 30, top=nav_y)
            self.screen.blit(right_text, right_rect)
        else:
            start_text = self.text_font.render("ENTER para comecar!", True, self.accent_color)
            start_rect = start_text.get_rect(center=(WIDTH // 2, nav_y + 5))
            alpha = int(200 + 55 * math.sin(self.anim_time * 4))
            start_text.set_alpha(alpha)
            self.screen.blit(start_text, start_rect)
        
        skip_text = self.small_font.render("ESC - Pular Tutorial", True, self.dim_text)
        skip_rect = skip_text.get_rect(center=(WIDTH // 2, 25))
        self.screen.blit(skip_text, skip_rect)
        
    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            self.anim_time += dt
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                    
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return True
                    elif event.key == pygame.K_RETURN:
                        if self.page == self.max_pages - 1:
                            return True
                    elif event.key in (pygame.K_RIGHT, pygame.K_d):
                        if self.page < self.max_pages - 1:
                            self.page += 1
                    elif event.key in (pygame.K_LEFT, pygame.K_a):
                        if self.page > 0:
                            self.page -= 1
            
            self.screen.fill(self.bg_color)
            
            if self.page == 0:
                self.draw_page_0_welcome()
            elif self.page == 1:
                self.draw_page_1_controls()
            elif self.page == 2:
                self.draw_page_2_mechanics()
            elif self.page == 3:
                self.draw_page_3_tips()
            
            self.draw_page_indicators()
            self.draw_navigation()
            
            pygame.display.flip()
        
        return True


def show_tutorial():
    tutorial = TutorialScreen()
    return tutorial.run()
