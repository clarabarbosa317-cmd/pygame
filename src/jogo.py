import pygame
from os import path

from settings import TITULO, WIDTH, HEIGHT, FPS, LEVEL_TIMES, DEFAULT_LEVEL_TIME, TIMER_OK, TIMER_WARN, TIMER_DANG, BG, LEVEL_NAMES
from assets import load_player_sprites, load_sounds, load_backgrounds
from sprites import Player
from level import load_level, build_level_surface
from menu import show_menu
from tutorial import show_tutorial

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

        # Sistema de áudio
        self.music_channel = pygame.mixer.Channel(0)  # Canal dedicado para música
        self.music_volume = 0.15
        self.sfx_volume = 1.0

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
        self.enemies = pygame.sprite.Group()

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
            "enemies": self.enemies,
        })

        # Cria surface do nível (apenas tiles/objetos, transparente)
        self.level_surface = build_level_surface(self.all_tiles)

        # Fundo da fase atual (pode faltar)
        self.current_background = self.backgrounds.get(self.current_level)

        # Cria ou reposiciona jogadores
        if not hasattr(self, 'p1'):
            self.p1 = Player(spawns["red"][0], spawns["red"][1], "red", self.player_frames["red"], self.sounds)
            self.p2 = Player(spawns["blue"][0], spawns["blue"][1], "blue", self.player_frames["blue"], self.sounds)
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
        
        # Pause state
        self.paused = False
        self.pause_ticks = 0
        
        # Inicia música do nível
        self.play_level_music()

    def show_victory_screen(self):
        """Mostra tela de vitória melhorada com animações"""
        import math
        import random
        
        victory = True
        anim_time = 0.0
        
        # Cria estrelas/partículas de celebração
        particles = []
        for _ in range(50):
            particles.append({
                'x': random.randint(0, WIDTH),
                'y': random.randint(-HEIGHT, 0),
                'speed': random.uniform(1, 3),
                'size': random.randint(2, 5),
                'color': random.choice([
                    (255, 255, 100),  # Amarelo
                    (255, 200, 100),  # Laranja
                    (100, 255, 255),  # Ciano
                    (255, 100, 255),  # Rosa
                    (100, 255, 100),  # Verde
                ])
            })
        
        while victory:
            dt = self.clock.tick(FPS) / 1000.0
            anim_time += dt
            
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

            # Background gradiente
            for y in range(HEIGHT):
                ratio = y / HEIGHT
                r = int(20 + (50 - 20) * ratio)
                g = int(20 + (30 - 20) * ratio)
                b = int(60 + (80 - 60) * ratio)
                pygame.draw.line(self.screen, (r, g, b), (0, y), (WIDTH, y))
            
            # Atualiza e desenha partículas
            for particle in particles:
                particle['y'] += particle['speed']
                if particle['y'] > HEIGHT:
                    particle['y'] = -10
                    particle['x'] = random.randint(0, WIDTH)
                
                # Desenha estrela
                pygame.draw.circle(self.screen, particle['color'], 
                                 (int(particle['x']), int(particle['y'])), 
                                 particle['size'])
            
            # Painel central
            panel_w, panel_h = 700, 400
            panel_x = (WIDTH - panel_w) // 2
            panel_y = (HEIGHT - panel_h) // 2
            
            # Sombra do painel
            shadow_surf = pygame.Surface((panel_w + 10, panel_h + 10), pygame.SRCALPHA)
            pygame.draw.rect(shadow_surf, (0, 0, 0, 100), (0, 0, panel_w + 10, panel_h + 10), border_radius=20)
            self.screen.blit(shadow_surf, (panel_x + 5, panel_y + 5))
            
            # Painel principal
            panel_surf = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
            pygame.draw.rect(panel_surf, (40, 40, 70, 230), (0, 0, panel_w, panel_h), border_radius=20)
            pygame.draw.rect(panel_surf, (255, 215, 0), (0, 0, panel_w, panel_h), 5, border_radius=20)
            self.screen.blit(panel_surf, (panel_x, panel_y))
            
            # Título com efeito pulsante
            pulse = 1.0 + 0.1 * math.sin(anim_time * 3)
            title_font = pygame.font.Font(None, 100)
            title_text = "🏆 VITÓRIA! 🏆"
            
            # Sombra do título
            title_shadow = title_font.render(title_text, True, (0, 0, 0))
            title_shadow_scaled = pygame.transform.scale(
                title_shadow, 
                (int(title_shadow.get_width() * pulse), int(title_shadow.get_height() * pulse))
            )
            shadow_rect = title_shadow_scaled.get_rect(center=(WIDTH // 2 + 3, panel_y + 80 + 3))
            self.screen.blit(title_shadow_scaled, shadow_rect)
            
            # Título principal
            title = title_font.render(title_text, True, (255, 215, 0))
            title_scaled = pygame.transform.scale(
                title, 
                (int(title.get_width() * pulse), int(title.get_height() * pulse))
            )
            title_rect = title_scaled.get_rect(center=(WIDTH // 2, panel_y + 80))
            self.screen.blit(title_scaled, title_rect)
            
            # Linha decorativa
            line_y = panel_y + 140
            pygame.draw.line(self.screen, (255, 215, 0), 
                           (panel_x + 50, line_y), 
                           (panel_x + panel_w - 50, line_y), 3)
            
            # Mensagem principal
            msg1 = self.font.render("Parabéns!", True, (255, 255, 255))
            msg1_rect = msg1.get_rect(center=(WIDTH // 2, panel_y + 180))
            self.screen.blit(msg1, msg1_rect)
            
            msg2 = self.small_font.render("Você completou todos os 6 níveis!", True, (200, 255, 200))
            msg2_rect = msg2.get_rect(center=(WIDTH // 2, panel_y + 220))
            self.screen.blit(msg2, msg2_rect)
            
            # Dinossauros comemorando (animados)
            dino_bounce = abs(math.sin(anim_time * 4)) * 10
            
            # Dinossauro vermelho
            if hasattr(self, 'p1'):
                dino_red = self.p1.frames_right[int(anim_time * 8) % len(self.p1.frames_right)]
                dino_red_scaled = pygame.transform.scale(dino_red, (60, 60))
                self.screen.blit(dino_red_scaled, (panel_x + 80, panel_y + 260 - dino_bounce))
            
            # Dinossauro azul
            if hasattr(self, 'p2'):
                dino_blue = self.p2.frames_right[int(anim_time * 8) % len(self.p2.frames_right)]
                dino_blue_scaled = pygame.transform.scale(dino_blue, (60, 60))
                self.screen.blit(dino_blue_scaled, (panel_x + panel_w - 140, panel_y + 260 - dino_bounce))
            
            # Texto "Equipe Perfeita!"
            team_text = self.small_font.render("🤝 Equipe Perfeita! 🤝", True, (255, 200, 100))
            team_rect = team_text.get_rect(center=(WIDTH // 2, panel_y + 280))
            self.screen.blit(team_text, team_rect)
            
            # Instruções com efeito pulsante
            inst_alpha = int(200 + 55 * math.sin(anim_time * 4))
            inst1 = self.small_font.render("ENTER - Jogar Novamente", True, (100, 255, 100))
            inst1.set_alpha(inst_alpha)
            inst1_rect = inst1.get_rect(center=(WIDTH // 2, panel_y + 340))
            self.screen.blit(inst1, inst1_rect)
            
            inst2 = self.small_font.render("ESC - Sair do Jogo", True, (255, 100, 100))
            inst2_rect = inst2.get_rect(center=(WIDTH // 2, panel_y + 370))
            self.screen.blit(inst2, inst2_rect)

            pygame.display.flip()

    def show_timeover_screen(self):
        """Mostra tela quando o tempo acaba"""
        self.music_channel.stop()
        self.play_sfx('defeat')
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
                        start_game, show_tut = show_menu()
                        if show_tut:
                            if show_tutorial():
                                self.current_level = 1
                                self.load_current_level()
                        elif start_game:
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

    def play_sfx(self, sound_name):
        """Toca um efeito sonoro"""
        if sound_name in self.sounds:
            self.sounds[sound_name].play()
    
    def play_level_music(self):
        """Inicia música do nível atual"""
        if 'music' in self.sounds and self.current_level in self.sounds['music']:
            music = self.sounds['music'][self.current_level]
            music.set_volume(self.music_volume)
            self.music_channel.play(music, loops=-1)

    def check_level_complete(self):
        """Conclui quando os dois jogadores estão no portal correto"""
        return self.p1.in_goal and self.p2.in_goal

    def advance_level(self):
        """Avança para o próximo nível ou mostra vitória."""
        self.play_sfx('victory')
        self.current_level += 1
        if self.current_level > self.total_levels:
            self.show_victory_screen()
        else:
            self.load_current_level()
    
    def show_pause_menu(self):
        """Mostra menu de pausa com design melhorado"""
        # Pausa a música
        self.music_channel.pause()
        
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))  # Semi-transparent black
        
        # Panel for menu
        panel_w, panel_h = 500, 400
        panel_x = (WIDTH - panel_w) // 2
        panel_y = (HEIGHT - panel_h) // 2
        
        paused = True
        anim_time = 0.0
        
        while paused and self.running:
            dt = self.clock.tick(FPS) / 1000.0
            anim_time += dt
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    paused = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE or event.key == pygame.K_p:
                        paused = False
                        self.paused = False
                        self.music_channel.unpause()  # Retoma música
                    elif event.key == pygame.K_r:
                        # Restart level
                        self.music_channel.unpause()
                        self.load_current_level()
                        paused = False
                        self.paused = False
                    elif event.key == pygame.K_q:
                        self.music_channel.unpause()
                        start_game, show_tut = show_menu()
                        if show_tut:
                            if show_tutorial():
                                self.current_level = 1
                                self.load_current_level()
                        elif start_game:
                            self.current_level = 1
                            self.load_current_level()
                        else:
                            self.running = False
                        paused = False
                        self.paused = False
            
            # Draw game state underneath
            if getattr(self, 'current_background', None) is not None:
                self.screen.blit(self.current_background, (0, 0))
            else:
                self.screen.fill(BG)
            self.screen.blit(self.level_surface, (0, 0))
            self.players.draw(self.screen)
            self.draw_ui()
            
            # Draw pause overlay
            self.screen.blit(overlay, (0, 0))
            
            # Draw panel
            panel_surf = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
            pygame.draw.rect(panel_surf, (35, 40, 55, 240), (0, 0, panel_w, panel_h), border_radius=20)
            pygame.draw.rect(panel_surf, (100, 200, 255), (0, 0, panel_w, panel_h), 4, border_radius=20)
            self.screen.blit(panel_surf, (panel_x, panel_y))
            
            # Draw pause title with pulsing effect
            import math
            pulse = 1.0 + 0.1 * math.sin(anim_time * 3)
            title = self.font.render("|| PAUSADO", True, (255, 255, 255))
            title_scaled = pygame.transform.scale(title, (int(title.get_width() * pulse), int(title.get_height() * pulse)))
            title_rect = title_scaled.get_rect(center=(WIDTH // 2, panel_y + 70))
            self.screen.blit(title_scaled, title_rect)
            
            # Menu options with icons (usando símbolos simples que funcionam)
            options = [
                (">", "ESC/P", "Continuar", (100, 220, 100)),
                ("R", "R", "Reiniciar Nivel", (220, 180, 100)),
                ("X", "Q", "Voltar ao Menu", (220, 100, 100))
            ]
            
            y_offset = panel_y + 160
            for icon, key, text, color in options:
                # Icon
                icon_surf = self.font.render(icon, True, color)
                self.screen.blit(icon_surf, (panel_x + 50, y_offset - 5))
                
                # Key
                key_surf = self.small_font.render(f"[{key}]", True, (180, 180, 180))
                self.screen.blit(key_surf, (panel_x + 120, y_offset + 5))
                
                # Text
                text_surf = self.small_font.render(text, True, (220, 220, 220))
                self.screen.blit(text_surf, (panel_x + 200, y_offset + 5))
                
                y_offset += 70
            
            pygame.display.flip()

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE or event.key == pygame.K_p:
                        self.paused = True
                        self.pause_ticks = pygame.time.get_ticks()
                        self.show_pause_menu()
                        # Adjust timer for pause duration
                        pause_duration = (pygame.time.get_ticks() - self.pause_ticks) / 1000.0
                        self.level_start_ticks += int(pause_duration * 1000)

            # Atualiza timer do nível
            elapsed = (pygame.time.get_ticks() - self.level_start_ticks) / 1000.0
            self.level_time_left = max(0.0, self.level_time_limit - elapsed)
            if self.level_time_limit > 0 and self.level_time_left <= 0.0:
                self.show_timeover_screen()
                continue

            keys = pygame.key.get_pressed()

            # Atualiza tiles animados (portais) e inimigos
            for tile in self.all_tiles:
                if hasattr(tile, 'update'):
                    tile.update(dt)
            
            for enemy in self.enemies:
                enemy.update(dt)

            # Atualiza jogadores (se não estiver no delay de conclusão)
            if self.level_complete_timer <= 0:
                self.p1.update(keys, self.solids, self.color_tiles, self.hazards,
                               self.doors, self.ramps, (pygame.K_a, pygame.K_d, pygame.K_w), dt)
                self.p2.update(keys, self.solids, self.color_tiles, self.hazards,
                               self.doors, self.ramps, (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP), dt)
                
                # Verifica colisão com inimigos
                if pygame.sprite.spritecollide(self.p1, self.enemies, False):
                    self.p1._respawn()
                if pygame.sprite.spritecollide(self.p2, self.enemies, False):
                    self.p2._respawn()

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
            self.enemies.draw(self.screen)  # Desenha inimigos
            self.players.draw(self.screen)
            self.draw_ui()

            pygame.display.flip()

        pygame.quit()


if __name__ == "__main__":
    ret = show_menu()

if isinstance(ret, tuple):
    start_game, show_tut = ret
else:
    start_game = bool(ret)
    show_tut = True  # ou False, conforme você quiser o padrão

if start_game:
    game = Game()
    if show_tut:
        if not show_tutorial():
            pygame.quit()
            raise SystemExit
    game.run()
else:
    pygame.quit()
