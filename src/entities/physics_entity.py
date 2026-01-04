from abc import ABC, abstractmethod
from typing import (
    TYPE_CHECKING,
    Dict,
    Literal,
    Set,
    Tuple,
)
import pygame
from constants import BASE_SPEED, GRAVITY
from .states.player_fsm import State
from pydebug import pgdebug_rect

if TYPE_CHECKING:
    from game import Game


T4Directions = Literal["up", "down", "left", "right"]
TContactSides = Dict[T4Directions, bool]


class PhysicsEntity(ABC):
    game: "Game" = None  # type: ignore
    __instances: Set["PhysicsEntity"] = set()

    def __init__(
        self,
        etype: str,
        pos: Tuple[int, int],
        size: Tuple[int, int],
        states: Dict[str, State],
        offset: Tuple[int, int] = (0, 0),
    ):
        super().__init__()

        self.states = states

        assert len(states.keys()) > 0
        default_state = "idle" if "idle" in self.states else list(self.states.keys())[0]
        self.current_state: State = self.states[default_state]

        self.animation = self.game.assets[etype + "/" + default_state]

        self.etype = etype

        self.velocity = pygame.Vector2()

        self.obey_gravity = True

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

    @classmethod
    def add(cls, instance: "PhysicsEntity"):
        cls.__instances.add(instance)

    @classmethod
    def remove(cls, instance: "PhysicsEntity"):
        cls.__instances.remove(instance)

    @classmethod
    def render_all(cls, dt: float):
        surface = cls.game.screen
        for bat in cls.__instances:
            bat.update(dt)
            bat.render(surface)

    def rect(self):
        return pygame.Rect(self.pos, self.size)

    def hitbox(self):
        x, y = self.pos
        ox, oy = self.offset
        new_w, new_h = self.size[0] - 2 * ox, self.size[1] - 2 * oy
        new_y = oy + y
        new_x = x + ox
        return pygame.Rect(new_x, new_y, new_w, new_h)

    def grounded(self):
        return self.contact_sides["down"]

    def set_state(self, new_state: str):
        if new_state != self.current_state.name:
            self.current_state = self.states[new_state]
            self.animation = self.game.assets[self.etype + "/" + new_state].copy()

    def manage_state(self):
        next_state = self.current_state.can_transition(self)
        if next_state is not None:
            self.current_state.exit(self)
            self.set_state(next_state)
            self.current_state.enter(self)
        self.current_state.update(self)

    def collision_horizontal(self):
        tiles = self.game.tilemap.physics_rect_around(self.pos)
        hitbox = self.hitbox()

        for tile in tiles:
            if tile.colliderect(hitbox):
                self.__resolve_horizontal_collision(hitbox, tile)
                break

    def __resolve_horizontal_collision(
        self, hitbox: pygame.Rect, tile_rect: pygame.Rect, /
    ):
        if self.velocity.x < 0:
            self.pos.x += tile_rect.right - hitbox.left
        elif self.velocity.x > 0:
            self.pos.x -= hitbox.right - tile_rect.left
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

    @abstractmethod
    def handle_movement(self, dt: float):
        pass

    def update(self, dt: float):
        self.handle_movement(dt)
        self.identify_contact_sides()
        self.manage_state()
        self.animation.update()

    def render(self, surface: pygame.Surface):
        frame = self.animation.get_frame()
        render_pos = self.pos - self.game.scroll

        if self.flipped:
            frame = pygame.transform.flip(frame, True, False)

        render_pos.x += (self.size[0] - frame.get_width()) / 2
        render_pos.y += (self.size[1] - frame.get_height()) / 2
        hitbox = self.hitbox()
        pos = hitbox.topleft - self.game.scroll
        size = hitbox.size
        surface.blit(frame, render_pos)
        pgdebug_rect(surface, (pos, size))
