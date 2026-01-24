import math
from abc import ABC, abstractmethod
from typing import Dict, Generic, Optional, Tuple, TypeVar, cast, override

from pygame import Vector2
from pygame.surface import Surface
from pytmx.pytmx import pygame

from entities.air_entity import AirEntity
from entities.base_entity import BaseEntity
from entities.ground_entity import GroundEntity
from entities.states import bat_fsm as bat_fsm
from entities.states import mushroom_fsm as mus_fsm
from entities.states.base_fsm import State
from pydebug import pgdebug
from ttypes.index_type import TPosType
from ui.elements.healthbar import HealthbarUI
from utils.timer import Timer

TEntity = TypeVar("TEntity", bound="BaseEntity")


class Enemy(Generic[TEntity], ABC):
    def __init__(
        self,
        etype: str,
        hit_timer_ms: int,
        attack_timer_ms: int,
        chase_radius: int,
    ) -> None:
        self.target: Optional["BaseEntity"] = None
        self.hit_timer = Timer(hit_timer_ms, stale_init=True)
        self.attack_timer = Timer(attack_timer_ms, stale_init=True)
        self.chase_radius = chase_radius

        self.stats = {"health": 1.0, "damage": 0.1}

        self.healthbar = HealthbarUI(self, width=100, height=10)

    def set_target(self, target: "BaseEntity"):
        self.target = target

    def remove_target(self):
        self.target = None

    def is_target_vulnarable(self):
        hit_timer = cast(Optional[Timer], getattr(self.target, "hit_timer"))
        return hit_timer is not None and not hit_timer.has_reached_interval()

    @abstractmethod
    def can_chase(self, entity: "BaseEntity") -> bool: ...

    @abstractmethod
    def can_attack(self, entity: "BaseEntity") -> bool: ...

    def take_damage(self, amount: float) -> Optional[bool]:
        self.stats["health"] -= amount
        self.healthbar.on_alter(self.stats["health"])
        self.hit_timer.reset_to_now()


class Bat(AirEntity, Enemy["Bat"]):
    def __init__(
        self,
        pos: Tuple[int, int],
        size: Tuple[int, int],
        /,
        chase_radius: int = 500,
        attack_radius: Optional[int] = None,
        hit_timer_ms: int = 1000,
        attack_timer_ms: int = 1000,
        offset: Tuple[int, int] = (0, 0),
    ):
        states: Dict[str, State] = {
            "fly": bat_fsm.FlyState(),
            "chase": bat_fsm.ChaseState(),
            "attack": bat_fsm.AttackState(),
            "hit": bat_fsm.HitState(),
        }

        hit_animation = self.game.assets["bat" + "/" + "hit"]
        attack_animation = self.game.assets["bat" + "/" + "attack"]
        bat_hit_animation_time = int(hit_animation.frames_len * hit_animation.animation_speed * 1000)
        bat_attack_animation_time = int(attack_animation.frames_len * attack_animation.animation_speed * 1000)

        AirEntity.__init__(self, "bat", pos, size, states, offset)
        Enemy.__init__(
            self,
            etype="bat",
            attack_timer_ms=bat_hit_animation_time + hit_timer_ms,
            hit_timer_ms=bat_attack_animation_time + attack_timer_ms,
            chase_radius=chase_radius,
        )

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
        hit_animation = self.game.assets["mushroom" + "/" + "hit"]
        attack_animation = self.game.assets["mushroom" + "/" + "attack"]
        hit_animation_time = int(hit_animation.frames_len * hit_animation.animation_speed * 1000)
        attack_animation_time = int(attack_animation.frames_len * attack_animation.animation_speed * 1000)
        GroundEntity.__init__(self, "mushroom", pos, size, states, offset)
        Enemy.__init__(
            self,
            etype="mushroom",
            hit_timer_ms=hit_animation_time + hit_timer_ms,
            attack_timer_ms=attack_animation_time + attack_timer_ms,
            chase_radius=chase_radius,
        )

    def can_chase(self, entity: "BaseEntity"):
        distance_y = abs(entity.pos.y - self.pos.y)
        distance_x = entity.pos.x - self.pos.x
        return distance_y <= self.size[1] and abs(distance_x) <= self.chase_radius

    def can_attack(self, entity: "BaseEntity") -> bool:
        return self.rect().colliderect(entity.hitbox())

    def update(self, dt: float):
        self.healthbar.update()
        return super().update(dt)

    @override
    def render(self, surface: Surface, offset: TPosType):
        pgdebug(f"{self.hit_timer.has_reached_interval()}")
        self.healthbar.render(surface, offset)
        frame, pos = self.get_renderable(offset)

        if not self.hit_timer.has_reached_interval():
            frame_cp = frame.copy()

            t = pygame.time.get_ticks() * 0.02
            alpha = (math.sin(t) * 0.5 + 0.5) * 255

            frame_cp.set_alpha(int(alpha))
            surface.blit(frame_cp, pos)
        else:
            surface.blit(frame, pos)
