from abc import ABC, abstractmethod
from typing import Dict, Generic, Optional, Set, Tuple, Type, TypeVar

from pygame import Vector2

from entities.physics_entity import AirEntity, GroundEntity, PhysicsEntity
from entities.states.base_fsm import State
from entities.states.bat_fsm import FlyState, ChaseState, AttackState, HitState
from entities.states.mushroom_fsm import DeathState, IdleState
from entities.states.player_fsm import RunState
from utils.timer import Timer

TEntity = TypeVar("TEntity", bound="PhysicsEntity")


class Enemy(Generic[TEntity], ABC):
    def __init__(
        self,
        hit_timer_ms: int = 2000,
        attack_timer_ms: int = 1700,
        chase_radius: int = 500,
    ) -> None:
        self.target: Optional["PhysicsEntity"] = None
        self.hit_timer = Timer(hit_timer_ms)
        self.attack_timer = Timer(attack_timer_ms)
        self.chase_radius = chase_radius

    def set_target(self, target: "PhysicsEntity"):
        self.target = target

    def remove_target(self):
        self.target = None

    @abstractmethod
    def can_chase(self, entity: "PhysicsEntity") -> bool:
        ...

    @abstractmethod
    def can_attack(self, entity: "PhysicsEntity") -> bool:
        ...


class Bat(AirEntity, Enemy["Bat"]):
    def __init__(
        self,
        pos: Tuple[int, int],
        size: Tuple[int, int],
        /,
        offset: Tuple[int, int] = (0, 0),
        chase_radius: int = 500,
        attack_radius: Optional[int] = None,
        hit_timer_ms: int = 2000,
        attack_timer_ms: int = 1700,
    ):
        states: Dict[str, State] = {
            "fly": FlyState(),
            "chase": ChaseState(),
            "attack": AttackState(),
            "hit": HitState(),
        }
        AirEntity.__init__(self, "bat", pos, size, states, offset)
        Enemy.__init__(self, hit_timer_ms, attack_timer_ms, chase_radius)

        if self.current_state.name != "fly":
            self.set_state("fly")

        self.obey_gravity = False
        self.default_pos = Vector2(pos)

        self.attack_radius = attack_radius or self.hitbox().w // 2

    def can_chase(self, entity: "PhysicsEntity"):
        distance = self.pos.distance_to(entity.pos)
        return distance <= self.chase_radius

    def can_attack(self, entity: "PhysicsEntity"):
        distance = self.pos.distance_to(entity.pos)
        return distance <= self.attack_radius


class Mushroom(GroundEntity, Enemy["Mushroom"]):
    def __init__(
        self,
        pos: Tuple[int, int],
        size: Tuple[int, int],
        /,
        offset: Tuple[int, int] = (0, 0),
        hit_timer_ms: int = 2000,
        attack_timer_ms: int = 1700,
        chase_radius: int = 500,
    ):
        states = {
            "idle": IdleState(),
            "attack": AttackState(),
            "death": DeathState(),
            "hit": HitState(),
            "run": RunState(),
        }
        GroundEntity.__init__(self, "mushroom", pos, size, states, offset)
        Enemy.__init__(self, hit_timer_ms, attack_timer_ms, chase_radius)

    def can_chase(self, entity: "PhysicsEntity") -> bool:
        distance = self.pos.distance_to(entity.pos)
        return distance <= self.chase_radius

    def can_attack(self, entity: "PhysicsEntity") -> bool:
        return self.rect().colliderect(entity.hitbox())
