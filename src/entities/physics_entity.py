from typing import (
    Dict,
    Literal,
    Tuple,
)

import pygame

from entities.base_entity import BaseEntity
from entities.states.base_fsm import State

T4Directions = Literal["up", "down", "left", "right"]
TContactSides = Dict[T4Directions, bool]


class PhysicsEntity(BaseEntity):
    velocity: pygame.Vector2
    contact_sides: TContactSides
    obey_gravity: bool

    def __init__(
        self,
        etype: str,
        pos: Tuple[int, int],
        size: Tuple[int, int],
        states: Dict[str, State],
        offset: Tuple[int, int] = (0, 0),
    ):
        super().__init__(etype, pos, size, states, offset)

        self.velocity = pygame.Vector2()
        self.obey_gravity = True

        self.contact_sides = {
            "left": False,
            "right": False,
            "up": False,
            "down": False,
        }

    def grounded(self):
        return self.contact_sides["down"]

    def collision_horizontal(self):
        tiles = self.game.tilemap.get_physics_rects(self.hitbox())
        hitbox = self.hitbox()

        for tile in tiles:
            if tile.colliderect(hitbox):
                self.__resolve_horizontal_collision(hitbox, tile)
                break

    def __resolve_horizontal_collision(self, hitbox: pygame.Rect, tile_rect: pygame.Rect):
        if self.velocity.x < 0:
            self.pos.x += tile_rect.right - hitbox.left
        elif self.velocity.x > 0:
            self.pos.x -= hitbox.right - tile_rect.left
        self.velocity.x = 0

    def collision_vertical(self):
        tiles = self.game.tilemap.get_physics_rects(self.hitbox())
        hitbox = self.hitbox()

        for tile in tiles:
            if tile.colliderect(hitbox):
                self.__resolve_vertical_collision(hitbox, tile)
                break

    def __resolve_vertical_collision(self, hitbox: pygame.Rect, tile_rect: pygame.Rect):
        if self.velocity.y < 0:
            self.pos.y += tile_rect.bottom - hitbox.top
        elif self.velocity.y > 0:
            self.pos.y += tile_rect.top - hitbox.bottom
        self.velocity.y = 0

    def handle_movement(self, dt: float):
        from constants import BASE_SPEED, GRAVITY

        if self.obey_gravity:
            self.pos.x += self.velocity.x * (BASE_SPEED * dt)
            self.collision_horizontal()

            self.velocity.y += GRAVITY * dt
            self.pos.y += self.velocity.y * dt
            self.collision_vertical()
        else:
            self.pos.x += self.velocity.x * dt
            self.pos.y += self.velocity.y * dt

    def identify_contact_sides(self):
        tiles_rect_around = self.game.tilemap.get_physics_rects(self.hitbox())

        hitbox = self.hitbox()
        self.contact_sides["left"] = hitbox.move(-1, 0).collidelist(tiles_rect_around) >= 0
        self.contact_sides["right"] = hitbox.move(1, 0).collidelist(tiles_rect_around) >= 0
        self.contact_sides["down"] = hitbox.move(0, 1).collidelist(tiles_rect_around) >= 0
        self.contact_sides["up"] = hitbox.move(0, -1).collidelist(tiles_rect_around) >= 0

    def update(self, dt: float):
        self.handle_movement(dt)
        self.identify_contact_sides()
        super().update(dt)
