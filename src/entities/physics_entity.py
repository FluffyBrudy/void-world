from typing import TYPE_CHECKING, Dict, Literal, Sequence, Tuple, cast, override
import pygame
from constants import BASE_SPEED
from pydebug import pgdebug, pgdebug_rect
from utils.animation import Animation

if TYPE_CHECKING:
    from game import Game
    from pygame.typing import IntPoint


TBasicAction = Literal["idle", "run", "jump", "attack"]
T4Directions = Literal["up", "down", "left", "right"]


class PhysicsEntity:
    # fmt: off
    __slots__ = ("pos", "size", "velocity",
                 "collisions", "flipped", "action", 
                 "probe_offsets", "animation", "etype")
    # fmt: on
    game: "Game" = cast("Game", None)

    def __init__(self, etype: str, pos: "IntPoint") -> None:
        self.pos = pygame.Vector2(pos)
        self.action: TBasicAction = "idle"
        self.etype = etype
        self.flipped = False
        self.velocity = pygame.Vector2(0, 0)
        self.probe_offsets: Dict[T4Directions, Tuple[int, int]] = {
            "down": (0, 1),
            "left": (-1, 0),
            "right": (1, 0),
        }
        self.collisions: Dict[T4Directions, bool] = {
            "up": False,
            "down": False,
            "left": False,
            "right": False,
        }

        self.animation = self.game.assets[etype + "/" + self.action].copy()
        self.size = self.animation.get_frame().size

    @staticmethod
    def init_collision_state() -> Dict[T4Directions, bool]:
        return {
            "up": False,
            "down": False,
            "left": False,
            "right": False,
        }

    @property
    def rect(self):
        return pygame.Rect(self.pos, self.size)

    @property
    def hitbox(self):
        return self.rect

    def handle_vertical_collision(self, movement_y: float):
        tiles_around = self.game.tilemap.physics_rect_around(self.pos)

        entity_rect = self.hitbox.copy()
        for tile_rect in tiles_around:
            if tile_rect.colliderect(entity_rect):
                if movement_y > 0:
                    entity_rect.bottom = tile_rect.top
                    self.collisions["down"] = True
                    self.pos.y = entity_rect.y
                    break
                elif movement_y < 0:
                    entity_rect.top = tile_rect.bottom
                    self.collisions["up"] = True
                    self.pos.y = entity_rect.y
                    break

    def handle_horizontal_collision(self, movement_x: float):
        tiles_around = self.game.tilemap.physics_rect_around(self.pos)
        entity_rect = self.hitbox.copy()

        delta = 0
        for tile_rect in tiles_around:
            if tile_rect.colliderect(entity_rect):
                if movement_x > 0:
                    delta = tile_rect.left - entity_rect.right
                    self.collisions["right"] = True
                    self.pos.x += delta
                    break
                elif movement_x < 0:
                    delta = tile_rect.right - entity_rect.left
                    self.collisions["left"] = True
                    self.pos.x += delta
                    break

    def probe_collision(self):
        tiles_around = self.game.tilemap.physics_rect_around(self.pos)
        for side, offset in self.probe_offsets.items():
            probe_rect = self.hitbox.move(offset)
            for rect in tiles_around:
                if rect.colliderect(probe_rect):
                    self.collisions[side] = True

    def set_action(self, action: TBasicAction):
        if action != self.action:
            old_rect = self.hitbox.copy()
            self.action = action
            key = self.etype + "/" + action
            self.animation: "Animation" = self.game.assets[key].copy()

            new_size = self.animation.get_frame().get_size()
            self.size = new_size

            old_bottom_center = old_rect.midbottom
            self.pos.x = old_bottom_center[0] - self.size[0] / 2
            self.pos.y = old_bottom_center[1] - self.size[1]

    def manage_state(self, direction_x: int):
        if direction_x:
            self.set_action("run")
        else:
            self.set_action("idle")

    def apply_gravity(self):
        self.velocity.y = min(self.velocity.y + 0.1, 10)

    def update(self, dt: float, movement: "IntPoint" = (0, 0)):
        self.collisions = PhysicsEntity.init_collision_state()
        direction_x = movement[0]

        frame_movement_x = round(
            (direction_x + self.velocity.x) * (dt * BASE_SPEED * 1.5), 2
        )
        frame_movement_y = round(self.velocity.y * (dt * BASE_SPEED), 2)

        if direction_x < 0:
            self.flipped = True
        elif direction_x > 0:
            self.flipped = False

        self.pos.x += frame_movement_x
        self.handle_horizontal_collision(frame_movement_x)

        self.pos.y += frame_movement_y
        self.handle_vertical_collision(frame_movement_y)

        self.probe_collision()
        self.apply_gravity()
        if self.collisions["down"] or self.collisions["up"]:
            self.velocity.y = 0

        pgdebug(self.collisions)
        self.manage_state(movement[0])
        self.animation.update()

    def render(self):
        surface = self.game.screen
        pos = self.pos - self.game.scroll
        image = self.animation.get_frame()

        if self.flipped:
            image = pygame.transform.flip(image, True, False)
        pgdebug_rect(image, (0, 0, *self.size), 1, 1)
        surface.blit(image, pos)


class Player(PhysicsEntity):
    def __init__(self, etype: str, pos: "IntPoint", offset: "IntPoint") -> None:
        super().__init__(etype, pos)
        offset_x, offset_y = offset

        def make_hitbox(
            frame_size: tuple[int, int], use_y_offset: bool = False
        ) -> tuple[int, int, int, int]:
            w, h = frame_size
            y_off = offset_y if use_y_offset else 0
            return (offset_x, y_off, w - 2 * offset_x, h - 2 * y_off)

        self.state_hitbox: Dict[TBasicAction, tuple[int, int, int, int]] = {
            "idle": make_hitbox(
                self.game.assets["player/idle"].get_frame().size, use_y_offset=True
            ),
            "run": make_hitbox(self.game.assets["player/run"].get_frame().size),
            "jump": make_hitbox(self.game.assets["player/jump"].get_frame().size),
            "attack": make_hitbox(self.game.assets["player/attack"].get_frame().size),
        }

        self.set_action("idle")

    @property
    def hitbox(self) -> pygame.Rect:
        ox, oy = self.pos
        hx, hy, hw, hh = self.state_hitbox[self.action]
        return pygame.Rect((ox + hx), (oy + hy), hw, hh)

    def jump(self):
        self.velocity.y = -3
