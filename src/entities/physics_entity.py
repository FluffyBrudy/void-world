from typing import (
    TYPE_CHECKING,
    Dict,
    Literal,
    Tuple,
    override,
)
import pygame
from constants import (
    BASE_SPEED,
    GRAVITY,
    JUMP_DISTANCE,
    MAX_FALL_SPEED,
    WALL_FRICTION_COEFFICIENT,
)
from lib.state import IdleState, JumpState, RunState, SlideState
from pydebug import pgdebug

if TYPE_CHECKING:
    from game import Game


T4Directions = Literal["up", "down", "left", "right"]
TContactSides = Dict[T4Directions, bool]


class PhysicsEntity:
    game: "Game" = None  # type: ignore

    def __init__(
        self,
        etype: str,
        pos: Tuple[int, int],
        size: Tuple[int, int],
        offset: Tuple[int, int] = (0, 0),
    ):
        super().__init__()

        self.states = {
            "idle": IdleState(),
            "run": RunState(),
            "jump": JumpState(),
            "wallslide": SlideState(),
        }
        self.current_state = self.states["idle"]

        self.animation = self.game.assets[etype + "/" + "idle"]

        self.etype = etype

        self.velocity = pygame.Vector2()

        self.flipped = False

        self.contact_sides: TContactSides = {
            "left": False,
            "right": False,
            "up": False,
            "down": False,
        }

        self.animation = self.game.assets[etype + "/" + self.current_state.name]

        self.offset = offset
        self.pos = pygame.Vector2(pos)
        self.size = size

    def rect(self):
        return pygame.Rect(self.pos, self.size)

    def hitbox(self):
        x, y = self.pos
        ox, oy = self.offset
        new_x, new_y = ox + x, oy + y
        new_w, new_h = self.size[0] - 2 * ox, self.size[1] - 2 * oy
        return pygame.Rect(new_x, new_y, new_w, new_h)

    def is_grounded(self):
        return self.contact_sides["down"]

    def set_state(self, new_state: str):
        if new_state != self.current_state.name:
            self.current_state = self.states[new_state]
            self.animation = self.game.assets[self.etype + "/" + new_state].copy()

    def manage_state(self):
        next_state = self.current_state.can_transition(self)
        if next_state is not None:
            self.set_state(next_state)

    def collision_horizontal(self):
        tiles_rect_around = self.game.tilemap.physics_rect_around(self.pos)

        for tile_rect in tiles_rect_around:
            hitbox = self.hitbox()
            if tile_rect.colliderect(hitbox):
                if self.velocity.x < 0:
                    self.pos.x = tile_rect.right - self.offset[0]
                    self.velocity.x = 0
                elif self.velocity.x > 0:
                    self.pos.x = tile_rect.left - self.hitbox().width - self.offset[0]
                    self.velocity.x = 0

    def collision_vertical(self):
        tiles_rect_around = self.game.tilemap.physics_rect_around(self.pos)
        hitbox = self.hitbox()
        delta = 0

        for tile_rect in tiles_rect_around:
            if tile_rect.colliderect(hitbox):
                if self.velocity.y < 0:
                    delta = tile_rect.bottom - hitbox.top
                    self.velocity.y = 0
                elif self.velocity.y > 0:
                    delta = tile_rect.top - hitbox.bottom
                    self.velocity.y = 0
                self.pos[1] += delta
                break

    def identify_contact_sides(self):
        tiles_rect_around = self.game.tilemap.physics_rect_around(self.pos)

        hitbox = self.hitbox()
        self.contact_sides["left"] = (
            hitbox.move(-1, 0).collidelist(tiles_rect_around) >= 0
        )
        self.contact_sides["right"] = (
            hitbox.move(1, 0).collidelist(tiles_rect_around) >= 0
        )
        self.contact_sides["down"] = (
            hitbox.move(0, 1).collidelist(tiles_rect_around) >= 0
        )
        self.contact_sides["up"] = (
            hitbox.move(0, -1).collidelist(tiles_rect_around) >= 0
        )

    def handle_movement(self, dt: float):
        frame_movement_x = (self.velocity.x) * (BASE_SPEED * dt * 2)
        self.pos[0] += frame_movement_x
        self.collision_horizontal()

        self.velocity.y += GRAVITY * dt
        self.pos[1] += self.velocity.y * dt
        self.collision_vertical()

    def update(self, dt: float):
        self.handle_movement(dt)
        self.identify_contact_sides()
        self.manage_state()
        self.animation.update()

    def render(self):
        frame = self.animation.get_frame()
        if self.flipped:
            frame = pygame.transform.flip(frame, True, False)

        render_pos = self.pos - self.game.scroll
        self.game.screen.blit(frame, render_pos)


class Player(PhysicsEntity):
    def __init__(
        self,
        pos: Tuple[int, int],
        size: Tuple[int, int],
        offset: Tuple[int, int] = (0, 0),
    ):
        super().__init__("player", pos, size, offset)

    def input(self):
        keys = pygame.key.get_pressed()

        input_vector = pygame.Vector2(0, 0)
        if keys[pygame.K_LEFT]:
            input_vector.x -= 2
            self.flipped = True
        if keys[pygame.K_RIGHT]:
            input_vector.x += 2
            self.flipped = False
        if self.current_state.name in ("idle", "run") and keys[pygame.K_SPACE]:
            self.jump()

        if input_vector:
            self.velocity.x = input_vector.x
        else:
            self.velocity.x = 0

    def can_slide(self):
        return (
            self.velocity.y > 0
            and (self.contact_sides["left"] or self.contact_sides["right"])
            and not self.contact_sides["down"]
        )

    def jump(self):
        self.velocity.y = -JUMP_DISTANCE * 2

    @override
    def update(self, dt: float):
        self.input()
        if self.can_slide():
            self.velocity.y = min(
                self.velocity.y, MAX_FALL_SPEED * WALL_FRICTION_COEFFICIENT
            )

        super().update(dt)

    def manage_state(self):
        super().manage_state()
