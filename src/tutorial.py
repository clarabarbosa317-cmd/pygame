# tutorial.py
# In-game tutorial screens for DinoWars (pygame)
# Usage: from tutorial import Tutorial; Tutorial(...).run()

import pygame
from typing import Callable, Optional, Sequence, Dict, Any


class Tutorial:
    """
    A lightweight, drop-in tutorial overlay shown after the main menu.
    Does not mutate game state; returns a boolean to indicate whether
    the game should continue (True) or quit (False).
    """

    def __init__(
        self,
        screen: pygame.Surface,
        font: pygame.font.Font,
        small_font: pygame.font.Font,
        clock: pygame.time.Clock,
        fps: int = 60,
        show_menu_cb: Optional[Callable[[], bool]] = None,
    ) -> None:
        self.screen = screen
        self.font = font
        self.small_font = small_font
        self.clock = clock
        self.fps = int(fps)
        self.show_menu_cb = show_menu_cb

        # Tutorial content (3 pages)
        self.pages: Sequence[Dict[str, Any]] = (
            {
                "title": "Como jogar",
                "lines": (
                    "Objetivo: leve cada dinossauro ao portal da sua cor.",
                    "Vermelho → portal VERMELHO (G) | Azul → portal AZUL (H).",
                    "Conclui quando os DOIS estiverem nos seus portais.",
                ),
            },
            {
                "title": "Controles",
                "lines": (
                    "P1 (Vermelho): A / D para andar, W para pular.",
                    "P2 (Azul): ← / → para andar, ↑ para pular.",
                    "Dica: coordene os pulos e use as rampas.",
                ),
            },
            {
                "title": "Cenário e Regras",
                "lines": (
                    "Blocos (#), Rampas (/ e \\), Espinhos (X).",
                    "Tiles R/B: só a cor correspondente pode pisar.",
                    "Caiu ou pisou na cor errada? Reaparece no spawn.",
                    "R - Reiniciar | ESC - Menu. Boa sorte!",
                ),
            },
        )

    def run(self) -> bool:
        """
        Render the tutorial, handle navigation, and exit when the user
        confirms start or decides to leave to the menu.
        Returns:
            True  -> continue to the game
            False -> user chose to quit from the menu or window closed
        """
        page = 0
        running_tutorial = True
        continue_game = True

        while running_tutorial:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running_tutorial = False
                    continue_game = False

                elif event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_RIGHT, pygame.K_d):
                        page = (page + 1) % len(self.pages)
                    elif event.key in (pygame.K_LEFT, pygame.K_a):
                        page = (page - 1) % len(self.pages)
                    elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        if page == len(self.pages) - 1:
                            running_tutorial = False  # start the game
                        else:
                            page = min(page + 1, len(self.pages) - 1)
                    elif event.key == pygame.K_ESCAPE:
                        # Optionally bounce to the menu, then decide whether to continue.
                        if self.show_menu_cb is not None:
                            if not self.show_menu_cb():
                                continue_game = False
                        running_tutorial = False

            self._draw_frame(page)
            pygame.display.flip()
            self.clock.tick(self.fps)

        return continue_game

    # -------------------- Internal helpers -------------------- #

    def _draw_frame(self, page_index: int) -> None:
        sw, sh = self.screen.get_width(), self.screen.get_height()
        self.screen.fill((15, 18, 28))

        # Panel
        panel_w, panel_h = int(sw * 0.86), int(sh * 0.7)
        panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        panel.fill((0, 0, 0, 188))
        prect = panel.get_rect(center=(sw // 2, sh // 2))
        self.screen.blit(panel, prect)

        # Title
        page = self.pages[page_index]
        title_surf = self.font.render(page["title"], True, (255, 255, 150))
        self.screen.blit(title_surf, title_surf.get_rect(midtop=(sw // 2, prect.top + 24)))

        # Lines
        y = prect.top + 92
        for line in page["lines"]:
            txt = self.small_font.render("• " + str(line), True, (230, 230, 230))
            self.screen.blit(txt, txt.get_rect(x=prect.left + 32, y=y))
            y += 42

        # Footer
        nav = self.small_font.render(
            "← / → navegar  |  ENTER avançar  |  ESC menu",
            True,
            (200, 200, 200),
        )
        self.screen.blit(nav, nav.get_rect(midbottom=(sw // 2, prect.bottom - 20)))

        # Page indicator
        indicator = self.small_font.render(f"{page_index + 1}/{len(self.pages)}", True, (160, 200, 255))
        self.screen.blit(indicator, indicator.get_rect(bottomright=(prect.right - 16, prect.bottom - 16)))
