from typing import Dict, Tuple

from pygame import Vector2

from constants import BASE_SPEED
from entities.physics_entity import PhysicsEntity
from entities.states.player_fsm import State
from utils.math_utils import circle_collision


class Bat(PhysicsEntity):
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

    def update(self, dt: float):
        player = self.game.player
        collided = circle_collision(self.pos, player.pos, 500, 50)
        if collided[0]:
            vector_dir = (player.pos - self.pos).normalize()
            self.velocity = vector_dir * BASE_SPEED
            self.flipped = True if vector_dir.x < 0 else False
            if collided[1]:
                self.velocity.x = 0
                self.velocity.y = 0
                self.set_state("attack")
        elif self.default_pos.distance_squared_to(self.pos) >= 9:  # for tolorance
            self.set_state("fly")
            vector_dir = (self.default_pos - self.pos).normalize()
            self.velocity = vector_dir * BASE_SPEED
            self.flipped = True if vector_dir.x < 0 else False
        else:
            self.velocity.x = 0
            self.velocity.y = 0
            self.set_state("fly")
        super().update(dt)
