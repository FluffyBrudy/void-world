from typing import Dict, Tuple

from constants import BASE_SPEED, GRAVITY
from entities.physics_entity import PhysicsEntity
from entities.states.player_fsm import State


class GroundEntity(PhysicsEntity):
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
        frame_movement_x = (self.velocity.x) * (BASE_SPEED * dt)
        self.pos[0] += frame_movement_x
        self.collision_horizontal()

        self.velocity.y += GRAVITY * dt
        self.pos[1] += self.velocity.y * dt
        self.collision_vertical()
