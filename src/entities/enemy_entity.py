from abc import ABC, abstractmethod
from random import uniform
from typing import TYPE_CHECKING, Callable, Dict, Optional, Tuple, cast

from pygame import Vector2
from pygame.surface import Surface

from entities.base_entity import BaseEntity
from entities.physics_entity import PhysicsEntity
from entities.projectile.fire import FireProjectile
from entities.states import bat_fsm as bat_fsm
from entities.states import ground_enemy_fsm
from entities.states.base_fsm import State
from managers.asset_manager import assets_manager
from ttypes.index_type import TPosType
from ui.widgets.healthbar import HealthbarUI
from utils.combat_utils import horizontal_range, melee_range
from utils.timer import Timer

if TYPE_CHECKING:
    from game import Game


class Enemy(PhysicsEntity, ABC):
    game: "Game" = None  # type: ignore

    def __init__(
        self,
        etype: str,
        pos: Tuple[int, int],
        size: Tuple[int, int],
        states: Dict[str, State],
        offset: Tuple[int, int] = (0, 0),
        hit_timer_ms: int = 0,
        attack_timer_ms: int = 0,
        chase_radius: int = 400,
        attack_check: Callable[[BaseEntity, BaseEntity], bool] = melee_range,
    ) -> None:
        super().__init__(etype, pos, size, states, offset)

        self.target: Optional[BaseEntity] = None
        self.chase_radius = chase_radius
        self.stats.update({"health": 1.0, "damage": 0.1})

        hit_anim = assets_manager.assets[f"{etype}/hit"]
        attack_anim = assets_manager.assets[f"{etype}/attack"]

        anim_hit_ms = int(hit_anim.frames_len * hit_anim.animation_speed * 1000)
        anim_attack_ms = int(attack_anim.frames_len * attack_anim.animation_speed * 1000)

        self.hit_timer = Timer(hit_timer_ms + anim_hit_ms, stale_init=True)
        self.attack_timer = Timer(attack_timer_ms + anim_attack_ms, stale_init=True)

        self.healthbar = HealthbarUI(self, visibility_timer=self.hit_timer.interval, width=100, height=10)

        self._attack_check = attack_check

    def set_target(self, target: BaseEntity):
        self.target = target

    def remove_target(self):
        self.target = None

    def is_target_vulnarable(self):
        if not self.target:
            return False
        hit_timer = cast(Optional[Timer], getattr(self.target, "hit_timer"))
        return hit_timer is not None and not hit_timer.has_reached_interval()

    @abstractmethod
    def can_chase(self, entity: BaseEntity) -> bool: ...

    def can_attack(self, entity: BaseEntity) -> bool:
        return self._attack_check(self, entity)

    def take_damage(self, amount: float) -> Optional[bool]:
        self.stats["health"] -= amount
        self.healthbar.on_alter(self.stats["health"])
        self.hit_timer.reset_to_now()

    def render(self, surface: Surface, offset: TPosType):
        self.healthbar.render(surface, offset)
        frame, pos = self.get_renderable(offset)

        if not self.hit_timer.has_reached_interval() and self.get_state() != "death":
            frame_cp = frame.copy()

            t = uniform(0.1, 0.9)
            alpha = int(t * 255)

            frame_cp.set_alpha(int(alpha))
            surface.blit(frame_cp, pos)
        else:
            surface.blit(frame, pos)


class Bat(Enemy):
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
            "attack": bat_fsm.AttackState(startup_frame=7, active_frame=3),
            "hit": bat_fsm.HitState(),
        }

        super().__init__(
            etype="bat",
            pos=pos,
            size=size,
            states=states,
            offset=offset,
            attack_timer_ms=hit_timer_ms,
            hit_timer_ms=attack_timer_ms,
            chase_radius=chase_radius,
        )

        if self.current_state.name != "fly":
            self.set_state("fly")

        self.obey_gravity = False
        self.default_pos = Vector2(pos)

        self.attack_radius = attack_radius or self.hitbox().w // 2

    def can_chase(self, entity: BaseEntity):
        distance = self.pos.distance_to(entity.pos)
        return distance <= self.chase_radius

    def can_attack(self, entity: BaseEntity):
        distance = self.pos.distance_to(entity.pos)
        return distance <= self.attack_radius

    def update(self, dt: float):
        self.healthbar.update()
        return super().update(dt)


class Mushroom(Enemy):
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
            "idle": ground_enemy_fsm.IdleState(),
            "attack": ground_enemy_fsm.AttackState(startup_frame=6, active_frame=2),
            "death": ground_enemy_fsm.DeathState(),
            "hit": ground_enemy_fsm.HitState(),
            "run": ground_enemy_fsm.RunState(),
        }
        super().__init__(
            etype="mushroom",
            pos=pos,
            size=size,
            states=states,
            offset=offset,
            hit_timer_ms=hit_timer_ms,
            attack_timer_ms=attack_timer_ms,
            chase_radius=chase_radius,
        )
        self.obey_gravity = True

    def can_chase(self, entity: BaseEntity):
        distance_y = abs(entity.pos.y - self.pos.y)
        distance_x = entity.pos.x - self.pos.x
        return distance_y <= self.size[1] and abs(distance_x) <= self.chase_radius

    def can_attack(self, entity: BaseEntity) -> bool:
        return super().can_attack(entity)

    def update(self, dt: float):
        self.healthbar.update()
        return super().update(dt)


class FireWorm(Enemy):
    def __init__(
        self,
        pos: Tuple[int, int],
        size: Tuple[int, int],
        /,
        offset: Tuple[int, int] = (0, 0),
        hit_timer_ms: int = 2000,
        attack_timer_ms: int = 1700,
        chase_radius: int = 800,
    ):
        states = {
            "idle": ground_enemy_fsm.IdleState(),
            "attack": ground_enemy_fsm.WormAttackState(),
            "death": ground_enemy_fsm.DeathState(),
            "hit": ground_enemy_fsm.HitState(),
            "run": ground_enemy_fsm.RunState(),
        }
        super().__init__(
            etype="fireworm",
            pos=pos,
            size=size,
            states=states,
            offset=offset,
            hit_timer_ms=hit_timer_ms,
            attack_timer_ms=attack_timer_ms,
            chase_radius=chase_radius,
            attack_check=lambda self_, target: horizontal_range(
                self_, target, max_x=chase_radius // 2, max_y=self.size[1]
            ),
        )
        self.obey_gravity = True

    def get_distance_to(self, entity: BaseEntity):
        distance_y = abs(entity.pos.y - self.pos.y)
        distance_x = entity.pos.x - self.pos.x
        return (distance_x, distance_y)

    def can_chase(self, entity: BaseEntity):
        distance_x, distance_y = self.get_distance_to(entity)
        return distance_y <= self.size[1] and abs(distance_x) <= self.chase_radius

    def can_attack(self, entity: BaseEntity) -> bool:
        return super().can_attack(entity)

    def shoot_fireball(self):
        hbox = self.hitbox()
        pos = hbox.midleft if self.flipped else hbox.midright
        vel = (-5, 0) if self.flipped else (5, 0)
        FireProjectile(pos, vel, 1000)

    def update(self, dt: float):
        self.healthbar.update()
        return super().update(dt)
