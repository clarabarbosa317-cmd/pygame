import pygame
from os import path

from settings import TITULO, WIDTH, HEIGHT, FPS
from assets import load_player_sprites, load_sounds
from sprites import Player
from level import load_level, build_level_surface
from menu import show_menu

class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(TITULO)
        self.clock = pygame.time.Clock()

        # Sistema de níveis
        self.current_level = 1
        self.total_levels = 6
        self.level_complete_timer = 0
        self.level_complete_delay = 1.0  # 2 segundos antes de avançar

        # Assets
        self.player_frames = load_player_sprites()
        self.sounds = load_sounds()

        # Fonte para UI
        self.font = pygame.font.Font(None, 48)
        self.small_font = pygame.font.Font(None, 32)

        self.running = True
        
        # Carrega o primeiro nível
        self.load_current_level()

    def load_current_level(self):
        """Carrega o nível atual"""
        # Limpa grupos anteriores
        self.all_tiles = pygame.sprite.Group()
        self.solids = pygame.sprite.Group()
        self.color_tiles = pygame.sprite.Group()
        self.hazards = pygame.sprite.Group()
        self.doors = pygame.sprite.Group()
        self.ramps = pygame.sprite.Group()

        # Caminho do nível
        level_filename = f"level{self.current_level}.txt"
        level_path = path.abspath(path.join(path.dirname(__file__), "..", "levels", level_filename))

        # Carrega o nível
        spawns = load_level(level_path, {
            "all_tiles": self.all_tiles,
            "solids": self.solids,
            "color_tiles": self.color_tiles,
            "hazards": self.hazards,
            "doors": self.doors,
            "ramps": self.ramps,
        })

        # Cria surface do nível
        self.level_surface = build_level_surface(self.all_tiles)

        # Cria ou reposiciona jogadores
        if not hasattr(self, 'p1'):
            self.p1 = Player(spawns["red"][0], spawns["red"][1], "red", self.player_frames["red"])
            self.p2 = Player(spawns["blue"][0], spawns["blue"][1], "blue", self.player_frames["blue"])
            self.players = pygame.sprite.Group(self.p1, self.p2)
        else:
            # Reposiciona jogadores existentes
            self.p1.rect.midbottom = spawns["red"]
            self.p1.spawn.update(spawns["red"])
            self.p1._respawn()
            
            self.p2.rect.midbottom = spawns["blue"]
            self.p2.spawn.update(spawns["blue"])
            self.p2._respawn()

        # Reseta timer de conclusão
        self.level_complete_timer = 0

        print(f"\n{'='*50}")
        print(f"NÍVEL {self.current_level} CARREGADO")
        print(f"{'='*50}\n")

    def check_level_complete(self):
        """Verifica se o nível foi completado"""
        return self.p1.in_goal and self.p2.in_goal

    def advance_level(self):
        """Avança para o próximo nível"""
        if self.current_level < self.total_levels:
            self.current_level += 1
            self.load_current_level()
        else:
            # Jogo completo!
            print("\n" + "="*50)
            print("🎉 PARABÉNS! VOCÊ COMPLETOU TODOS OS NÍVEIS! 🎉")
            print("="*50 + "\n")
            self.show_victory_screen()

    def reset_level(self):
        """Reinicia o nível atual"""
        for p in (self.p1, self.p2):
            p._respawn()
        self.level_complete_timer = 0

    def show_victory_screen(self):
        """Mostra tela de vitória"""
        victory = True
        while victory:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    victory = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                        victory = False
                    elif event.key == pygame.K_RETURN:
                        # Reinicia do nível 1
                        self.current_level = 1
                        self.load_current_level()
                        victory = False

            # Desenha tela de vitória
            self.screen.fill((20, 20, 40))
            
            # Título
            title = self.font.render("VITÓRIA!", True, (255, 255, 100))
            title_rect = title.get_rect(center=(WIDTH // 2, HEIGHT // 3))
            self.screen.blit(title, title_rect)

            # Mensagem
            msg = self.small_font.render("Você completou todos os 6 níveis!", True, (200, 200, 200))
            msg_rect = msg.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            self.screen.blit(msg, msg_rect)

            # Instruções
            inst1 = self.small_font.render("ENTER - Jogar novamente", True, (150, 150, 150))
            inst1_rect = inst1.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 80))
            self.screen.blit(inst1, inst1_rect)

            inst2 = self.small_font.render("ESC - Sair", True, (150, 150, 150))
            inst2_rect = inst2.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 120))
            self.screen.blit(inst2, inst2_rect)

            pygame.display.flip()
            self.clock.tick(FPS)

    def draw_ui(self):
        """Desenha interface do usuário"""
        # Nível atual
        level_text = self.font.render(f"Nível {self.current_level}/{self.total_levels}", True, (255, 255, 255))
        self.screen.blit(level_text, (10, 10))

        # Instruções (canto inferior)
        help_text = self.small_font.render("R - Reiniciar | ESC - Menu", True, (200, 200, 200))
        help_rect = help_text.get_rect(bottomleft=(10, HEIGHT - 10))
        self.screen.blit(help_text, help_rect)

        # Se nível completo, mostra mensagem
        if self.level_complete_timer > 0:
            complete_text = self.font.render("NÍVEL COMPLETO!", True, (100, 255, 100))
            complete_rect = complete_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            
            # Fundo semi-transparente
            s = pygame.Surface((complete_rect.width + 40, complete_rect.height + 20))
            s.set_alpha(200)
            s.fill((0, 0, 0))
            self.screen.blit(s, (complete_rect.x - 20, complete_rect.y - 10))
            
            self.screen.blit(complete_text, complete_rect)

            # Próximo nível ou vitória
            if self.current_level < self.total_levels:
                next_text = self.small_font.render(f"Próximo: Nível {self.current_level + 1}", True, (200, 200, 200))
            else:
                next_text = self.small_font.render("Último nível completado!", True, (255, 255, 100))
            
            next_rect = next_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))
            self.screen.blit(next_text, next_rect)

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        self.reset_level()
                    elif event.key == pygame.K_ESCAPE:
                        # Volta ao menu
                        if show_menu():
                            self.current_level = 1
                            self.load_current_level()
                        else:
                            self.running = False

            keys = pygame.key.get_pressed()

            # Atualiza tiles animados (portais)
            for tile in self.all_tiles:
                if hasattr(tile, 'update'):
                    tile.update(dt)

            # Atualiza jogadores apenas se não estiver no delay de conclusão
            if self.level_complete_timer <= 0:
                self.p1.update(keys, self.solids, self.color_tiles, self.hazards, 
                             self.doors, self.ramps, (pygame.K_a, pygame.K_d, pygame.K_w), dt)
                self.p2.update(keys, self.solids, self.color_tiles, self.hazards, 
                             self.doors, self.ramps, (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP), dt)

            # Verifica conclusão do nível
            if self.check_level_complete() and self.level_complete_timer <= 0:
                self.level_complete_timer = self.level_complete_delay

            # Timer de conclusão
            if self.level_complete_timer > 0:
                self.level_complete_timer -= dt
                if self.level_complete_timer <= 0:
                    self.advance_level()

            # Desenha tudo
            self.screen.blit(self.level_surface, (0, 0))
            self.players.draw(self.screen)
            self.draw_ui()
            
            pygame.display.flip()

        pygame.quit()


if __name__ == "__main__":
    # Mostra o menu primeiro
    if show_menu():
        # Se o jogador escolheu iniciar, roda o jogo
        Game().run()
    else:
        # Se escolheu sair, apenas encerra
        pygame.quit()