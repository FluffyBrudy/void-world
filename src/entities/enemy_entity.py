import math
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Dict, Generic, Optional, Tuple, TypeVar, cast

from pygame import Vector2
from pygame.surface import Surface
from pytmx.pytmx import pygame

from entities.air_entity import AirEntity
from entities.base_entity import BaseEntity
from entities.ground_entity import GroundEntity
from entities.states import bat_fsm as bat_fsm
from entities.states import mushroom_fsm as mus_fsm
from entities.states.base_fsm import State
from ttypes.index_type import TPosType
from ui.widgets.healthbar import HealthbarUI
from utils.timer import Timer

if TYPE_CHECKING:
    from game import Game

TEntity = TypeVar("TEntity", bound="BaseEntity")


class Enemy(Generic[TEntity], ABC):
    game: "Game" = None  # type: ignore

    def __init__(
        self,
        etype: str,
        hit_timer_ms: int = 0,
        attack_timer_ms: int = 0,
        chase_radius: int = 400,
    ) -> None:
        self.target: Optional["BaseEntity"] = None
        self.chase_radius = chase_radius
        self.stats = {"health": 1.0, "damage": 0.1}

        hit_anim = self.game.assets[f"{etype}/hit"]
        attack_anim = self.game.assets[f"{etype}/attack"]

        anim_hit_ms = int(hit_anim.frames_len * hit_anim.animation_speed * 1000)
        anim_attack_ms = int(attack_anim.frames_len * attack_anim.animation_speed * 1000)

        self.hit_timer = Timer(hit_timer_ms + anim_hit_ms, stale_init=True)
        self.attack_timer = Timer(attack_timer_ms + anim_attack_ms, stale_init=True)

        self.healthbar = HealthbarUI(self, visibility_timer=self.hit_timer.interval, width=100, height=10)

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

    def render(self, surface: Surface, offset: TPosType):
        self_as_entity: BaseEntity = cast(BaseEntity, self)
        self.healthbar.render(surface, offset)
        frame, pos = self_as_entity.get_renderable(offset)

        if not self.hit_timer.has_reached_interval():
            frame_cp = frame.copy()

            t = math.radians(pygame.time.get_ticks() % 360)
            alpha = (math.sin(t) + 0.5) * 255

            frame_cp.set_alpha(int(alpha))
            surface.blit(frame_cp, pos)
        else:
            surface.blit(frame, pos)


class Bat(Enemy["Bat"], AirEntity):
    def __init__(
        self,
        pos: Tuple[int, int],
        size: Tuple[int, int],
        /,
        chase_radius: int = 500,
        attack_radius: Optional[int] = None,
        hit_timer_ms: int = 2000,
        attack_timer_ms: int = 1700,
        offset: Tuple[int, int] = (0, 0),
    ):
        states: Dict[str, State] = {
            "fly": bat_fsm.FlyState(),
            "chase": bat_fsm.ChaseState(),
            "attack": bat_fsm.AttackState(),
            "hit": bat_fsm.HitState(),
        }

        AirEntity.__init__(self, "bat", pos, size, states, offset)
        Enemy.__init__(
            self,
            etype="bat",
            attack_timer_ms=hit_timer_ms,
            hit_timer_ms=attack_timer_ms,
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

    def update(self, dt: float):
        self.healthbar.update()
        return super().update(dt)


class Mushroom(Enemy["Mushroom"], GroundEntity):
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
        Enemy.__init__(
            self,
            etype="mushroom",
            hit_timer_ms=hit_timer_ms,
            attack_timer_ms=attack_timer_ms,
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


class FireWorm(Enemy["FireWorm"], GroundEntity):
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

        GroundEntity.__init__(self, "fireworm", pos, size, states, offset)
        Enemy.__init__(
            self,
            etype="fireworm",
            hit_timer_ms=hit_timer_ms,
            attack_timer_ms=attack_timer_ms,
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
