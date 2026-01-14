from typing import Dict, Optional, Set, Tuple

from pygame import Vector2

from entities.physics_entity import PhysicsEntity
from entities.states.base_fsm import State
from entities.states.bat_fsm import FlyState, ChaseState, AttackState, HitState
from pydebug import pgdebug
from utils.timer import Timer


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
        chase_radius=500,
        attack_radius=None,
    ):
        states: Dict[str, State] = {
            "fly": FlyState(),
            "chase": ChaseState(),
            "attack": AttackState(),
            "hit": HitState(),
        }
        super().__init__("bat", pos, size, states, offset)

        if self.current_state.name != "fly":
            self.set_state("fly")

        self.obey_gravity = False
        self.default_pos = Vector2(pos)
        self.hit_timer = Timer(2000)
        self.attack_timer = Timer(1700)

        self.target: Optional["PhysicsEntity"] = None

        self.attack_radius = attack_radius or self.hitbox().w // 2
        self.chase_radius = chase_radius

    def set_target(self, target: "PhysicsEntity"):
        self.target = target

    def remove_target(self):
        self.target = None

    def handle_movement(self, dt: float):
        self.pos.x += self.velocity.x * dt
        self.pos.y += self.velocity.y * dt

    def can_chase(self, entity: "PhysicsEntity"):
        """In case needed to check externally, dont use internally"""
        distance = self.pos.distance_to(entity.pos)
        return distance <= self.chase_radius

    def can_attack(self, entity: "PhysicsEntity"):
        """In case needed to check externally, dont use internally"""
        distance = self.pos.distance_to(entity.pos)
        return distance <= self.attack_radius
