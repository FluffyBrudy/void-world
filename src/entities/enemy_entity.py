from abc import ABC, abstractmethod
from typing import Dict, Generic, Optional, Tuple, TypeVar, cast

from pygame import Vector2

from entities.air_entity import AirEntity
from entities.base_entity import BaseEntity
from entities.ground_entity import GroundEntity
from entities.physics_entity import PhysicsEntity
from entities.states.base_fsm import State
from entities.states import bat_fsm as bat_fsm
from entities.states import mushroom_fsm as mus_fsm
from pydebug import pgdebug
from utils.timer import Timer

TEntity = TypeVar("TEntity", bound="BaseEntity")


class Enemy(Generic[TEntity], ABC):
    def __init__(
        self,
        hit_timer_ms: int = 2000,
        attack_timer_ms: int = 1700,
        chase_radius: int = 500,
    ) -> None:
        self.target: Optional["BaseEntity"] = None
        self.hit_timer = Timer(hit_timer_ms)
        self.attack_timer = Timer(attack_timer_ms)
        self.chase_radius = chase_radius

    def set_target(self, target: "BaseEntity"):
        self.target = target

    def remove_target(self):
        self.target = None

    def is_target_vulnarable(self):
        hit_timer = cast(Optional[Timer], getattr(self.target, "hit_timer"))
        return hit_timer is not None and not hit_timer.has_reach_interval()

    @abstractmethod
    def can_chase(self, entity: "BaseEntity") -> bool:
        ...

    @abstractmethod
    def can_attack(self, entity: "BaseEntity") -> bool:
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
            "fly": bat_fsm.FlyState(),
            "chase": bat_fsm.ChaseState(),
            "attack": bat_fsm.AttackState(),
            "hit": bat_fsm.HitState(),
        }
        AirEntity.__init__(self, "bat", pos, size, states, offset)
        Enemy.__init__(self, hit_timer_ms, attack_timer_ms, chase_radius)

        if self.current_state.name != "fly":
            self.set_state("fly")

        self.obey_gravity = False
        self.default_pos = Vector2(pos)

        self.attack_radius = attack_radius or self.hitbox().w // 2

    def can_chase(self, entity: "BaseEntity"):
        distance = self.pos.distance_to(entity.pos)
        return distance <= self.chase_radius

    def can_attack(self, entity: "BaseEntity"):
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
        chase_radius: int = 400,
    ):
        states = {
            "idle": mus_fsm.IdleState(),
            "attack": mus_fsm.AttackState(),
            "death": mus_fsm.DeathState(),
            "hit": mus_fsm.HitState(),
            "run": mus_fsm.RunState(),
        }
        GroundEntity.__init__(self, "mushroom", pos, size, states, offset)
        Enemy.__init__(self, hit_timer_ms, attack_timer_ms, chase_radius)

    def can_chase(self, entity: "BaseEntity"):
        distance_y = abs(entity.pos.y - self.pos.y)
        distance_x = entity.pos.x - self.pos.x
        return distance_y <= self.size[1] and abs(distance_x) <= self.chase_radius

    def can_attack(self, entity: "BaseEntity") -> bool:
        return self.rect().colliderect(entity.hitbox())

    def update(self, dt: float):
        pgdebug(f"state={self.get_state()}")
        return super().update(dt)
