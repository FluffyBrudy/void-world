from typing import TYPE_CHECKING

from constants import BASE_SPEED
from entities.player import Player
from entities.states.base_fsm import State

if TYPE_CHECKING:
    from entities.enemy_entity import Mushroom


class IdleState(State["Mushroom"]):
    def __init__(self):
        super().__init__("idle")

    def enter(self, entity: "Mushroom"):
        pass

    def exit(self, entity: "Mushroom"):
        pass

    def update(self, entity: "Mushroom", **kwargs):
        pass

    def can_transition(self, entity: "Mushroom"):
        if entity.velocity.x != 0:
            return "run"
        return None


class ChaseState(State["Mushroom"]):
    def __init__(self):
        super().__init__("chase")

    def update(self, entity: "Mushroom", **kwargs):
        if entity.target is None:
            return None

        if not entity.attack_timer.has_reach_interval():
            entity.velocity *= 0
            return

        distance_x = entity.target.pos.x - entity.pos.x
        distance_y = entity.target.pos.y - entity.pos.y

        if abs(distance_y) > entity.size[0]:
            return
        if abs(distance_x) <= entity.chase_radius:
            entity.velocity.x = distance_x * min(BASE_SPEED, distance_x)
            entity.flipped = distance_x < 0

    def can_transition(self, entity: "Mushroom"):
        if entity.target is None:
            return "idle"

        if isinstance(entity.target, Player):
            if not entity.target.hit_timer.has_reach_interval():
                entity.velocity *= 0
                return "idle"

        distance_x = entity.target.pos.x - entity.pos.x
        if abs(distance_x) <= entity.chase_radius:
            return "run"
        if (
            entity.can_attack(entity.target)
            and entity.attack_timer.has_reach_interval()
        ):
            return "attack"

        return None


class AttackState(State["Mushroom"]):
    def __init__(self):
        super().__init__("attack")

    def enter(self, entity: "Mushroom"):
        entity.velocity *= 0

    def can_transition(self, entity: "Mushroom"):
        if entity.target is None:
            return "idle"

        if not entity.animation.has_animation_end():
            return None

        return "idle"


class HitState(State["Mushroom"]):
    def __init__(self):
        super().__init__("attack")

    def enter(self, entity: "Mushroom"):
        entity.velocity *= 0

    def can_transition(self, entity: "Mushroom"):
        if entity.target is None:
            return "idle"

        if not entity.animation.has_animation_end():
            return None

        return "idle"


class DeathState(State["Mushroom"]):
    def __init__(self):
        super().__init__("Death")

    def enter(self, entity: "Mushroom"):
        entity.velocity *= 0

    def can_transition(self, entity: "Mushroom"):
        if entity.animation.has_animation_end():
            type(entity).remove(entity)
        return None
