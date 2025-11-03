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

        # Grupos
        self.all_tiles   = pygame.sprite.Group()
        self.solids      = pygame.sprite.Group()
        self.color_tiles = pygame.sprite.Group()
        self.hazards     = pygame.sprite.Group()
        self.doors       = pygame.sprite.Group()
        self.ramps       = pygame.sprite.Group()   # <<< NOVO

        self.player_frames = load_player_sprites()
        self.sounds = load_sounds()

        level_path = path.abspath(path.join(path.dirname(__file__), "..", "levels", "level1.txt"))
        spawns = load_level(level_path, {
            "all_tiles": self.all_tiles,
            "solids": self.solids,
            "color_tiles": self.color_tiles,
            "hazards": self.hazards,
            "doors": self.doors,
            "ramps": self.ramps,        # <<< NOVO
        })

        self.level_surface = build_level_surface(self.all_tiles)

        self.p1 = Player(spawns["red"][0],  spawns["red"][1],  "red",  self.player_frames["red"])
        self.p2 = Player(spawns["blue"][0], spawns["blue"][1], "blue", self.player_frames["blue"])
        self.players = pygame.sprite.Group(self.p1, self.p2)

        self.running = True

    def check_level_complete(self):
        return self.p1.in_goal and self.p2.in_goal

    def reset_level(self):
        for p in (self.p1, self.p2):
            p._respawn()

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                    self.reset_level()

            keys = pygame.key.get_pressed()

            self.p1.update(keys, self.solids, self.color_tiles, self.hazards, self.doors, self.ramps,
                           (pygame.K_a, pygame.K_d, pygame.K_w), dt)
            self.p2.update(keys, self.solids, self.color_tiles, self.hazards, self.doors, self.ramps,
                           (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP), dt)

            if self.check_level_complete():
                print("LEVEL COMPLETE!")
                self.reset_level()

            self.screen.blit(self.level_surface, (0, 0))
            self.players.draw(self.screen)
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
