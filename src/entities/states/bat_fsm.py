from typing import TYPE_CHECKING, Type
from constants import BASE_SPEED
from entities.player import Player
from entities.states.base_fsm import State


if TYPE_CHECKING:
    from entities.enemy_entity import Bat


class FlyState(State["Bat"]):
    def __init__(self):
        super().__init__("fly")

    def enter(self, entity: "Bat") -> None:
        pass

    def update(self, entity: "Bat", **kwargs):
        if entity.target is None:
            return

        if not entity.attack_timer.has_reach_interval():
            entity.velocity *= 0
            return

        distance = entity.default_pos.distance_to(entity.pos)
        if distance == 0:
            return
        vector_dir = (entity.default_pos - entity.pos).normalize()
        entity.velocity = vector_dir * min(BASE_SPEED, distance)
        entity.flipped = vector_dir.x < 0

    def can_transition(self, entity: "Bat"):
        if entity.target is None:
            return None

        distance = (entity.pos).distance_to(entity.target.pos)
        if distance <= entity.chase_radius:
            return "chase"
        return None


class ChaseState(State["Bat"]):
    def __init__(self):
        super().__init__("chase")

    def update(self, entity: "Bat", **kwargs):
        if entity.target is None:
            return None

        if not entity.attack_timer.has_reach_interval():
            entity.velocity *= 0
            return

        distance = (entity.target.pos).distance_to(entity.pos)
        vector_dir = (entity.target.pos - entity.pos).normalize()
        if distance < 1:
            entity.velocity = vector_dir * BASE_SPEED
        else:
            entity.velocity = vector_dir * BASE_SPEED
        if distance > entity.size[0] // 2:
            entity.flipped = entity.velocity.x < 0

    def can_transition(self, entity: "Bat"):
        if entity.target is None:
            return None

        if entity.is_target_vulnarable():
            entity.velocity *= 0
            return None

        distance = (entity.pos).distance_to(entity.target.pos)
        if distance > entity.chase_radius:
            return "fly"
        if (
            distance <= entity.attack_radius
            and entity.attack_timer.has_reach_interval()
        ):
            return "attack"

        return None


class AttackState(State["Bat"]):
    def __init__(self):
        super().__init__("attack")

    def enter(self, entity: "Bat") -> None:
        entity.attack_timer.reset_to_now()
        entity.velocity *= 0

    def update(self, entity: "Bat", **kwargs) -> None:
        if entity.target is None:
            return
        entity.flipped = entity.target.flipped

    def can_transition(self, entity: "Bat"):
        if entity.target is None:
            return None

        if not entity.animation.has_animation_end():
            return None

        if entity.animation.has_animation_end():
            return "fly"

        distance = (entity.pos).distance_to(entity.target.pos)

        if distance > entity.chase_radius:
            return "fly"

        if distance > entity.attack_radius:
            return "chase"

        return None

    def exit(self, entity: "Bat") -> None:
        entity.velocity *= 0


class HitState(State["Bat"]):
    def __init__(self):
        super().__init__("hit")

    def enter(self, entity: "Bat") -> None:
        entity.hit_timer.reset_to_now()
        entity.velocity *= 0

    def can_transition(self, entity: "Bat"):
        if entity.hit_timer.has_reach_interval():
            return "fly"
        return None
