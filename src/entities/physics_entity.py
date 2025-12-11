from typing import TYPE_CHECKING, Dict, Literal, Sequence, Tuple, cast, override
import pygame
from constants import BASE_SPEED
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

    def __init__(self, etype: str, pos: Sequence[int], size: Tuple[int, int]) -> None:
        self.size = size
        self.pos = pygame.Vector2(pos)
        self.action: TBasicAction = "run"
        self.etype = etype
        self.flipped = False
        self.velocity = pygame.Vector2(0, 0)
        self.probe_offsets: Dict[T4Directions, Tuple[int, int]] = {
            "down": (0, 1),
            "left": (-1, 0),
            "right": (1, 0),
            "up": (0, -1),
        }
        self.collisions = {"up": False, "down": False, "left": False, "right": False}
        self.set_action("idle")

    @property
    def rect(self):
        return pygame.Rect(self.pos, self.size)

    def handle_vertical_collision(self, movement: "IntPoint"):
        pass

    def handle_horizontal_collision(self, movement: "IntPoint"):
        pass

    def set_action(self, action: TBasicAction):
        if action != self.action:
            self.action = action
            key = self.etype + "/" + action
            self.animation: "Animation" = self.game.assets[key].copy()

    def update(self, dt: float, movement: "IntPoint" = (0, 0)):
        direction_x = movement[0]
        frame_movement_x = round(
            (direction_x + self.velocity.x) * (dt * BASE_SPEED * 1.5), 2
        )
        frame_movement_y = round(self.velocity.y * (dt * BASE_SPEED * 1.5), 2)

        if direction_x < 0:
            self.flipped = True
        elif direction_x > 0:
            self.flipped = False

        self.pos += (frame_movement_x, frame_movement_y)
        # self.apply_gravity()

        if direction_x:
            self.set_action("run")
        else:
            self.set_action("idle")

        self.animation.update()

    def apply_gravity(self):
        self.velocity.y = min(self.velocity.y + 0.1, 10)

    def render(self):
        surface = self.game.screen
        pos = self.pos - self.game.scroll
        image = self.animation.get_frame()

        if self.flipped:
            image = pygame.transform.flip(image, True, False)

        surface.blit(image, pos)


class Player(PhysicsEntity):
    def __init__(self, etype: str, pos: Sequence[int], size: Tuple[int, int]) -> None:
        super().__init__(etype, pos, size)

        self.hitbox: Dict[TBasicAction, Tuple[int, int, int, int]] = {
            "idle": (91, 90, 8, 22),
            "run": (80, 92, 23, 20),
            "jump": (84, 86, 19, 19),
            "attack": (89, 91, 12, 21),
        }

    @property
    def rect(self) -> pygame.Rect:
        ox, oy = self.pos
        hx, hy, hw, hh = self.hitbox[self.action]
        return pygame.Rect((ox + hx), (oy + hy), hw, hh)

    def jump(self):
        self.velocity.y = -3
