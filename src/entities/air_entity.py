from typing import Dict, Tuple

from entities.physics_entity import PhysicsEntity
from entities.states.player_fsm import State


class AirEntity(PhysicsEntity):
    def __init__(
        self,
        etype: str,
        pos: Tuple[int, int],
        size: Tuple[int, int],
        states: Dict[str, State],
        offset: Tuple[int, int] = (0, 0),
    ):
        super().__init__(etype, pos, size, states, offset)

    def handle_movement(self, dt: float):
        self.pos.x += self.velocity.x * dt
        self.pos.y += self.velocity.y * dt
