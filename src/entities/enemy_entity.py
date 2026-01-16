from typing import Dict, Generic, Optional, Set, Tuple, TypeVar

from pygame import Vector2

from entities.physics_entity import AirEntity, GroundEntity, PhysicsEntity
from entities.states.base_fsm import State
from entities.states.bat_fsm import FlyState, ChaseState, AttackState, HitState
from pydebug import pgdebug
from utils.timer import Timer

TEntity = TypeVar("TEntity", bound="PhysicsEntity")


class Enemy(Generic[TEntity]):
    __group: Set[TEntity] = set()

    @classmethod
    def add_to_group(cls, instance: TEntity):
        cls.__group.add(instance)

    @classmethod
    def get_instances(cls):
        return cls.__group

    def __init__(self) -> None:
        self.target: Optional["PhysicsEntity"] = None

    def set_target(self, target: "PhysicsEntity"):
        self.target = target

    def remove_target(self):
        self.target = None


class Bat(AirEntity, Enemy["Bat"]):
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
        AirEntity.__init__(self, "bat", pos, size, states, offset)
        Enemy.__init__(self)

        if self.current_state.name != "fly":
            self.set_state("fly")

        self.obey_gravity = False
        self.default_pos = Vector2(pos)
        self.hit_timer = Timer(2000)
        self.attack_timer = Timer(1700)

        self.target: Optional["PhysicsEntity"] = None

        self.attack_radius = attack_radius or self.hitbox().w // 2
        self.chase_radius = chase_radius

    def can_chase(self, entity: "PhysicsEntity"):
        """In case needed to check externally, dont use internally"""
        distance = self.pos.distance_to(entity.pos)
        return distance <= self.chase_radius

    def can_attack(self, entity: "PhysicsEntity"):
        """In case needed to check externally, dont use internally"""
        distance = self.pos.distance_to(entity.pos)
        return distance <= self.attack_radius


class Mushroom(GroundEntity, Enemy["Mushroom"]):
    def __init__(
        self,
        pos: Tuple[int, int],
        size: Tuple[int, int],
        offset: Tuple[int, int] = (0, 0),
    ):
        states = {
            "idle": State("idle"),
            "attack": State("attack"),
            "death": State("death"),
            "hit": State("hit"),
            "run": State("run"),
        }
        GroundEntity.__init__(self, "mushroom", pos, size, states, offset)
        Enemy.__init__(self)
