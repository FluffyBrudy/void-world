from typing import (
    TYPE_CHECKING,
    Dict,
    Literal,
    Tuple,
    override,
)
import pygame
from pygame.sprite import Group, GroupSingle
from constants import (
    BASE_SPEED,
    GRAVITY,
    JUMP_DISTANCE,
    MAX_FALL_SPEED,
    WALL_FRICTION_COEFFICIENT,
)
from pydebug import pgdebug, pgdebug_rect
from utils.animation import Animation

if TYPE_CHECKING:
    from game import Game
    from pygame.typing import IntPoint


TBasicAction = Literal["idle", "run", "jump", "attack"]
T4Directions = Literal["up", "down", "left", "right"]
TContactSides = Dict[T4Directions, bool]


class PhysicsEntity:
    game: "Game" = None  # type: ignore

    def __init__(self, etype: str, pos: Tuple[int, int]):
        super().__init__()

        self.action: TBasicAction = "idle"
        self.animation = self.game.assets[etype + "/" + self.action]

        self.etype = etype
        self.image = self.animation.get_frame()

        self.rect = self.image.get_rect(topleft=pos)

        self.direction = pygame.Vector2()
        self.prev_direction = pygame.Vector2()

        self.friction = pygame.Vector2(0, 0)

        self.jumping = False

        self.contact_sides: TContactSides = {
            "left": False,
            "right": False,
            "up": False,
            "down": False,
        }

    def collision_horizontal(self):
        tiles_rect_around = self.game.tilemap.physics_rect_around(self.rect.topleft)

        for tile_rect in tiles_rect_around:
            if tile_rect.colliderect(self.rect):
                if self.direction.x < 0:
                    self.rect.left = tile_rect.right
                    break
                if self.direction.x > 0:
                    self.rect.right = tile_rect.left
                    break

    def collision_vertical(self):
        tiles_rect_around = self.game.tilemap.physics_rect_around(self.rect.topleft)
        for tile_rect in tiles_rect_around:
            if tile_rect.colliderect(self.rect):
                if self.direction.y < 0:
                    self.rect.top = tile_rect.bottom
                    self.direction.y = 0
                    break
                if self.direction.y > 0:
                    self.rect.bottom = tile_rect.top
                    self.direction.y = 0
                    break

    def identify_contact_sides(self):
        tiles_rect_around = self.game.tilemap.physics_rect_around(self.rect.topleft)
        self.contact_sides["left"] = (
            self.rect.move(-2, 0).collidelist(tiles_rect_around) >= 0
        )
        self.contact_sides["right"] = (
            self.rect.move(2, 0).collidelist(tiles_rect_around) >= 0
        )
        self.contact_sides["down"] = (
            self.rect.move(0, 2).collidelist(tiles_rect_around) >= 0
        )
        self.contact_sides["up"] = (
            self.rect.move(0, -2).collidelist(tiles_rect_around) >= 0
        )

    def handle_movement(self, dt: float):
        if self.contact_sides["down"]:
            self.jumping = False

        self.direction.y = self.direction.y + GRAVITY * dt

        frame_movement_x = (self.direction.x) * (BASE_SPEED * dt * 2)
        self.rect.x += round(frame_movement_x)
        self.collision_horizontal()

        self.rect.y += self.direction.y * dt
        self.collision_vertical()

    def update(self, dt: float):
        self.handle_movement(dt)
        self.identify_contact_sides()

    def render(self):
        main_surface = self.game.screen
        pos = self.rect.topleft - self.game.scroll
        main_surface.blit(self.image, pos)


class Player(PhysicsEntity):
    def __init__(self, pos: Tuple[int, int]):
        super().__init__("player", pos)

    def input(self):
        keys = pygame.key.get_pressed()

        input_vector = pygame.Vector2(0, 0)
        if keys[pygame.K_LEFT]:
            input_vector.x -= 1
        if keys[pygame.K_RIGHT]:
            input_vector.x += 1
        if not self.jumping and keys[pygame.K_SPACE]:
            self.jumping = True
            self.jump()

        if input_vector:
            self.direction.x = input_vector.x
        else:
            self.direction.x = 0

    def can_slide(self):
        return (
            self.direction.y > 0
            and (self.contact_sides["left"] or self.contact_sides["right"])
            and not self.contact_sides["down"]
        )

    def jump(self):
        self.direction.y = -JUMP_DISTANCE

    @override
    def update(self, dt: float):
        self.input()
        if self.can_slide():
            self.direction.y = min(
                self.direction.y, MAX_FALL_SPEED * WALL_FRICTION_COEFFICIENT
            )

        super().update(dt)
