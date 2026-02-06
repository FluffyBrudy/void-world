from typing import TYPE_CHECKING

from entities.states.base_fsm import State

if TYPE_CHECKING:
    from entities.enemy_entity import Enemy


class IdleState(State["Enemy"]):
    def __init__(self):
        super().__init__("idle")

    def enter(self, entity: "Enemy"):
        entity.velocity *= 0

    def can_transition(self, entity: "Enemy"):
        if entity.target is None:
            return None

        if entity.can_chase(entity.target) and not entity.is_target_vulnarable():
            return "run"

        return None


class RunState(State["Enemy"]):
    def __init__(self):
        super().__init__("run")

    def update(self, entity: "Enemy", **kwargs):
        if entity.target is None:
            return None

        distance_x = entity.target.pos.x - entity.pos.x
        if distance_x != 0:
            direction = distance_x / abs(distance_x)
        else:
            direction = 0

        entity.velocity.x = direction
        entity.flipped = distance_x < 0

    def can_transition(self, entity: "Enemy"):
        if entity.target is None:
            return None

        if entity.is_target_vulnarable():
            return "idle"

        if entity.can_attack(entity.target) and entity.attack_timer.has_reached_interval():
            return "attack"

        if not entity.can_chase(entity.target):
            return "idle"

        return None

    def exit(self, entity: "Enemy") -> None:
        entity.velocity.x *= 0


class AttackState(State["Enemy"]):
    def __init__(self):
        super().__init__("attack", 0, 0)

    def enter(self, entity: "Enemy"):
        entity.velocity *= 0

    def can_transition(self, entity: "Enemy"):
        if entity.target is None:
            return "idle"

        if not entity.animation.has_animation_end():
            return None

        return "idle"


class HitState(State["Enemy"]):
    def __init__(self):
        super().__init__("hit")

    def enter(self, entity: "Enemy"):
        entity.velocity.x *= 0

    def can_transition(self, entity: "Enemy"):
        if entity.stats["health"] <= 0.01:
            return "death"

        if entity.target is None:
            return "idle"

        if not entity.animation.has_animation_end():
            return None

        return "idle"


class DeathState(State["Enemy"]):
    def __init__(self):
        super().__init__("Death")

    def enter(self, entity: "Enemy"):
        entity.velocity *= 0

    def can_transition(self, entity: "Enemy"):
        if entity.animation.has_animation_end():
            entity.alive = False
        return None
