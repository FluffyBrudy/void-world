from typing import Dict, Set, Tuple
from entities.physics_entity import PhysicsEntity
from entities.states.enemy_fsm import Attack, FlyState, Hit
from entities.states.player_fsm import State


class Bat(PhysicsEntity):
    __instances: Set["Bat"] = set()

    def __init__(
        self,
        pos: Tuple[int, int],
        size: Tuple[int, int],
        offset: Tuple[int, int] = (0, 0),
    ):
        states: Dict[str, State] = {"fly": FlyState(), "attack": Attack(), "hit": Hit()}
        super().__init__("bat", pos, size, states, offset)
        self.current_state = states["fly"]
        self.gravity_scale = 0

    @classmethod
    def add(cls, instance: "Bat"):
        cls.__instances.add(instance)

    @classmethod
    def remove(cls, instance: "Bat"):
        cls.__instances.remove(instance)

    @classmethod
    def render_all(cls, dt: float):
        for bat in cls.__instances:
            bat.update(dt)
            bat.render()

    def render(self):
        return super().render()
