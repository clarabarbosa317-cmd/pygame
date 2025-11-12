import pygame
from settings import (
    TILE, NEUTRAL, RED, BLUE, HAZARD, GOAL_R, GOAL_B,
    MOVE_SPEED, JUMP_SPEED, GRAVITY, WIDTH, HEIGHT
)

class Tile(pygame.sprite.Sprite):
    """
    Tile genérico.
    slope: None | "up" (sobe p/ direita) | "down" (desce p/ direita)
    """
    def __init__(self, x, y, image=None, *, solid=False, deadly=False,
                 color_kind=None, goal_for=None, slope=None):
        super().__init__()
        self.solid = solid
        self.deadly = deadly
        self.color_kind = color_kind
        self.goal_for = goal_for
        self.slope = slope  # None | "up" | "down"

        if image is None:
            # fallback visual simples quando não vem textura
            color = NEUTRAL
            if deadly: color = HAZARD
            if goal_for == "red":  color = GOAL_R
            if goal_for == "blue": color = GOAL_B
            if color_kind == "red":  color = RED
            if color_kind == "blue": color = BLUE
            self.image = pygame.Surface((TILE, TILE))
            self.image.fill(color)
        else:
            self.image = image

        self.rect = self.image.get_rect(topleft=(x, y))

    # ------ Superfície da rampa ------
    # rampa_sobe  ("/"): superfície vai de baixo-esquerda -> topo-direita
    # rampa_desce ("\"): superfície vai de topo-esquerda  -> baixo-direita
    def surface_y(self, local_x):
        """Retorna Y (absoluto) da superfície da rampa dado x local [0..TILE-1]."""
        if self.slope is None:
            return None
        top = self.rect.top
        bottom = self.rect.bottom - 1
        lx = max(0, min(TILE - 1, int(local_x)))

        if self.slope == "up":      # sobe para a direita
            y = top + (TILE - 1 - lx)   # esquerda baixo, direita alto
        else:                        # "down": desce para a direita
            y = top + lx
        return y

    def y_at_world_x(self, world_x):
        """Conveniente: recebe x em coordenada de tela e devolve Y da superfície."""
        return self.surface_y(world_x - self.rect.left)


class AnimatedTile(pygame.sprite.Sprite):
    """
    Tile com animação (para portais, etc)
    """
    def __init__(self, x, y, frames, *, solid=False, deadly=False,
                 color_kind=None, goal_for=None):
        super().__init__()
        self.solid = solid
        self.deadly = deadly
        self.color_kind = color_kind
        self.goal_for = goal_for
        self.slope = None  # Tiles animados não são rampas
        
        self.frames = frames
        self.anim_index = 0.0
        self.anim_speed = 8.0  # frames por segundo
        
        self.image = self.frames[0]
        self.rect = self.image.get_rect(topleft=(x, y))
    
    def update(self, dt):
        """Atualiza a animação"""
        self.anim_index = (self.anim_index + self.anim_speed * dt) % len(self.frames)
        self.image = self.frames[int(self.anim_index)]


# ------------------- PLAYER -------------------
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, color_name, frames, sounds=None):
        super().__init__()
        self.color_name = color_name  # "red" | "blue"
        self.sounds = sounds or {}

        # animação
        self.frames_right = frames[:]
        self.frames_left  = [pygame.transform.flip(f, True, False) for f in frames]
        self.anim_index = 0.0
        self.anim_speed = 12.0
        self.facing = 1

        self.image = self.frames_right[0]
        self.rect = self.image.get_rect(midbottom=(x, y))

        # físicas
        self.pos = pygame.Vector2(self.rect.x, self.rect.y)
        self.vel = pygame.Vector2(0, 0)
        self.on_ground = False
        self.was_on_ground = False  # Para detectar pousos
        self.spawn = pygame.Vector2(self.rect.midbottom)

        self.in_goal = False

    def handle_input(self, keys, left, right, jump):
        self.vel.x = 0
        if keys[left]:
            self.vel.x = -MOVE_SPEED
            self.facing = -1
        if keys[right]:
            self.vel.x = MOVE_SPEED
            self.facing = 1
        if keys[jump] and self.on_ground:
            self.vel.y = -JUMP_SPEED
            self.on_ground = False
            # Som de pulo
            if 'jump' in self.sounds:
                self.sounds['jump'].play()

    def apply_gravity(self):
        self.vel.y += GRAVITY
        if self.vel.y > 24:
            self.vel.y = 24

    def collide_axis(self, solids, axis):
        hits = pygame.sprite.spritecollide(self, solids, False)
        for t in hits:
            if axis == "x":
                if self.vel.x > 0:
                    self.rect.right = t.rect.left
                elif self.vel.x < 0:
                    self.rect.left = t.rect.right
                self.pos.x = self.rect.x
            else:
                if self.vel.y > 0:
                    self.rect.bottom = t.rect.top
                    self.vel.y = 0
                    # Som de pousar (só se estava no ar)
                    if not self.on_ground and not self.was_on_ground and 'land' in self.sounds:
                        self.sounds['land'].play()
                    self.on_ground = True
                elif self.vel.y < 0:
                    self.rect.top = t.rect.bottom
                    self.vel.y = 0
                self.pos.y = self.rect.y

    def _respawn(self):
        # Som de morte
        if 'death' in self.sounds:
            self.sounds['death'].play()
        self.rect.midbottom = self.spawn
        self.pos.update(self.rect.x, self.rect.y)
        self.vel.update(0, 0)
        self.on_ground = False
        self.was_on_ground = False
        self.in_goal = False

    def check_underfoot(self, color_tiles, hazards):
        # piso imediatamente sob os pés
        self.rect.y += 1
        hits_color = pygame.sprite.spritecollide(self, color_tiles, False)
        hits_haz   = pygame.sprite.spritecollide(self, hazards, False)
        self.rect.y -= 1

        if hits_haz:
            self._respawn()
            return

        for t in hits_color:
            wrong = (
                (self.color_name == "red" and t.color_kind == "blue") or
                (self.color_name == "blue" and t.color_kind == "red")
            )
            if wrong:
                self._respawn()
                return

    def check_goal(self, doors):
        self.in_goal = False
        for d in pygame.sprite.spritecollide(self, doors, False):
            if d.goal_for == self.color_name:
                self.in_goal = True
                break

    def clamp_and_fall(self):
        self.rect.clamp_ip(pygame.Rect(0, 0, WIDTH, HEIGHT))
        self.pos.update(self.rect.x, self.rect.y)
        if self.rect.top > HEIGHT:
            self._respawn()

    # -------- Colisão com rampa (superfície inclinada) --------
    def collide_slopes(self, ramps):
        """
        Regras:
        - Considera rampas onde o player está em cima (overlap X e Y próximo).
        - Calcula Y da superfície na coluna do pé (centerx).
        - Se o pé atravessou a superfície, encaixa no Y e zera vel.y.
        """
        # Retângulo pequeno nos pés para limitar busca
        feet_rect = pygame.Rect(self.rect.centerx - self.rect.width // 4,
                                self.rect.bottom - 2,  # 2px acima da sola
                                self.rect.width // 2, 4)

        candidates = [r for r in ramps if r.rect.colliderect(feet_rect.inflate(TILE, TILE))]
        if not candidates:
            return

        # Ordena por Y do topo (a rampa mais alta primeiro) para evitar encaixe no tile errado
        candidates.sort(key=lambda r: r.rect.top)

        for r in candidates:
            # Só considera se verticalmente estamos dentro do tile
            if self.rect.bottom < r.rect.top - 1 or self.rect.top > r.rect.bottom:
                continue

            y_surface = r.y_at_world_x(self.rect.centerx)
            if y_surface is None:
                continue

            # Se atravessou a superfície (pé abaixo da linha), encosta na superfície
            if self.rect.bottom > y_surface >= r.rect.top:
                self.rect.bottom = int(y_surface)
                self.pos.y = self.rect.y
                self.vel.y = 0
                self.on_ground = True
                # Não damos break: pode haver duas rampas alinhadas; mas na prática 1 basta.
                # break

    def animate(self, dt):
        moving = abs(self.vel.x) > 0.01
        frames = self.frames_right if self.facing == 1 else self.frames_left
        if moving:
            self.anim_index = (self.anim_index + self.anim_speed * dt) % len(frames)
        else:
            self.anim_index = 0.0
        self.image = frames[int(self.anim_index)]

    def update(self, keys, solids, color_tiles, hazards, doors, ramps, controls, dt):
        left, right, jump = controls
        self.was_on_ground = self.on_ground
        self.handle_input(keys, left, right, jump)
        self.apply_gravity()

        # X
        self.pos.x += self.vel.x
        self.rect.x = round(self.pos.x)
        self.collide_axis(solids, "x")

        # Y
        self.pos.y += self.vel.y
        self.rect.y = round(self.pos.y)
        self.on_ground = False
        self.collide_axis(solids, "y")

        # Slope resolve DEPOIS da colisão vertical com sólidos
        self.collide_slopes(ramps)

        # Regras
        self.check_underfoot(color_tiles, hazards)
        self.check_goal(doors)
        self.clamp_and_fall()
        self.animate(dt)