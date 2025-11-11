import pygame
from os import path

from settings import TITULO, WIDTH, HEIGHT, FPS, LEVEL_TIMES, DEFAULT_LEVEL_TIME, TIMER_OK, TIMER_WARN, TIMER_DANG, BG
from assets import load_player_sprites, load_sounds, load_backgrounds
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
        self.level_complete_delay = 1.0  # atraso antes de avançar de fase

        # Assets
        self.player_frames = load_player_sprites()
        self.sounds = load_sounds()
        self.backgrounds = load_backgrounds()   # <<< fundos por fase

        # Fonte para UI
        self.font = pygame.font.Font(None, 48)
        self.small_font = pygame.font.Font(None, 32)

        self.running = True

        # Timer do nível (valores serão definidos em load_current_level)
        self.level_time_limit = 0
        self.level_start_ticks = 0
        self.level_time_left = 0.0

        # Carrega o primeiro nível (aqui configuramos o timer também)
        self.load_current_level()

    def load_current_level(self):
        """Carrega o nível atual e reseta tudo que é per-fase (inclui timer)."""
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

        # Carrega mapa para grupos, recebe posições de spawn
        spawns = load_level(level_path, {
            "all_tiles": self.all_tiles,
            "solids": self.solids,
            "color_tiles": self.color_tiles,
            "hazards": self.hazards,
            "doors": self.doors,
            "ramps": self.ramps,
        })

        # Cria surface do nível (apenas tiles/objetos, transparente)
        self.level_surface = build_level_surface(self.all_tiles)

        # Fundo da fase atual (pode faltar)
        self.current_background = self.backgrounds.get(self.current_level)

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

        # Define tempo do nível
        self.level_time_limit = LEVEL_TIMES.get(self.current_level, DEFAULT_LEVEL_TIME)
        self.level_start_ticks = pygame.time.get_ticks()
        self.level_time_left = float(self.level_time_limit)

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

            inst = self.small_font.render("ENTER - Reiniciar | ESC - Sair", True, (160, 160, 160))
            inst_rect = inst.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 60))
            self.screen.blit(inst, inst_rect)

            pygame.display.flip()
            self.clock.tick(FPS)

    def show_timeover_screen(self):
        """Mostra tela quando o tempo acaba"""
        timeover = True
        while timeover and self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    timeover = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                        timeover = False
                    elif event.key == pygame.K_RETURN:
                        # Volta ao menu
                        if show_menu():
                            self.current_level = 1
                            self.load_current_level()
                        else:
                            self.running = False
                        timeover = False

            self.screen.fill((40, 20, 20))
            title = self.font.render("TEMPO ESGOTADO", True, (255, 180, 180))
            title_rect = title.get_rect(center=(WIDTH // 2, HEIGHT // 3))
            self.screen.blit(title, title_rect)

            msg = self.small_font.render("O tempo acabou!", True, (220, 220, 220))
            msg_rect = msg.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            self.screen.blit(msg, msg_rect)

            inst = self.small_font.render("ENTER - Menu | ESC - Sair", True, (160, 160, 160))
            inst_rect = inst.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 60))
            self.screen.blit(inst, inst_rect)

            pygame.display.flip()
            self.clock.tick(FPS)

    def draw_ui(self):
        """Desenha interface do usuário"""
        # Nível atual
        level_text = self.font.render(f"Nível {self.current_level}/{self.total_levels}", True, (255, 255, 255))
        self.screen.blit(level_text, (10, 10))

        # Temporizador (canto superior direito)
        if self.level_time_limit > 0:
            secs = int(max(0, round(self.level_time_left)))
            mm = secs // 60
            ss = secs % 60
            timer_str = f"{mm:02d}:{ss:02d}"
            # Cor por urgência
            if secs <= 10:
                color = TIMER_DANG
            elif secs <= 20:
                color = TIMER_WARN
            else:
                color = TIMER_OK
            t_surf = self.font.render(timer_str, True, color)
            t_rect = t_surf.get_rect(topright=(WIDTH - 10, 10))
            self.screen.blit(t_surf, t_rect)

    def check_level_complete(self):
        """Conclui quando os dois jogadores estão no portal correto"""
        return self.p1.in_goal and self.p2.in_goal

    def advance_level(self):
        """Avança para o próximo nível ou mostra vitória."""
        self.current_level += 1
        if self.current_level > self.total_levels:
            self.show_victory_screen()
        else:
            self.load_current_level()

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            # Atualiza timer do nível
            elapsed = (pygame.time.get_ticks() - self.level_start_ticks) / 1000.0
            self.level_time_left = max(0.0, self.level_time_limit - elapsed)
            if self.level_time_limit > 0 and self.level_time_left <= 0.0:
                self.show_timeover_screen()
                continue

            keys = pygame.key.get_pressed()

            # Atualiza tiles animados (portais)
            for tile in self.all_tiles:
                if hasattr(tile, 'update'):
                    tile.update(dt)

            # Atualiza jogadores (se não estiver no delay de conclusão)
            if self.level_complete_timer <= 0:
                self.p1.update(keys, self.solids, self.color_tiles, self.hazards,
                               self.doors, self.ramps, (pygame.K_a, pygame.K_d, pygame.K_w), dt)
                self.p2.update(keys, self.solids, self.color_tiles, self.hazards,
                               self.doors, self.ramps, (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP), dt)

            # Verifica conclusão do nível
            if self.check_level_complete() and self.level_complete_timer <= 0:
                self.level_complete_timer = self.level_complete_delay

            # Timer de conclusão breve antes de avançar
            if self.level_complete_timer > 0:
                self.level_complete_timer -= dt
                if self.level_complete_timer <= 0:
                    self.advance_level()

            # Desenha tudo
            if getattr(self, 'current_background', None) is not None:
                self.screen.blit(self.current_background, (0, 0))
            else:
                self.screen.fill(BG)
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
