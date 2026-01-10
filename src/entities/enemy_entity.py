from typing import Dict, Set, Tuple

from pygame import Vector2

from constants import BASE_SPEED
from entities.physics_entity import PhysicsEntity
from entities.states.player_fsm import State
from utils.math_utils import circle_collision


class Bat(PhysicsEntity):
    __group: Set["Bat"] = set()

    @classmethod
    def add_to_group(cls, instance: "Bat"):
        cls.__group.add(instance)

    @classmethod
    def get_instances(cls):
        return cls.__group

    def __init__(
        self,
        pos: Tuple[int, int],
        size: Tuple[int, int],
        offset: Tuple[int, int] = (0, 0),
    ):
        states: Dict[str, State] = {
            "fly": State("fly"),
            "attack": State("attack"),
            "hit": State("hit"),
        }
        super().__init__("bat", pos, size, states, offset)
        self.current_state = states["fly"]
        self.obey_gravity = False
        self.default_pos = Vector2(pos)

    def handle_movement(self, dt: float):
        self.pos.x += self.velocity.x * dt

        self.pos.y += self.velocity.y * dt
