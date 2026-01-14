from typing import TYPE_CHECKING, Optional
from entities.states.base_fsm import State

if TYPE_CHECKING:
    from entities.player import Player


class IdleState(State):
    def __init__(self):
        super().__init__("idle")

    def enter(self, entity: "Player"):
        pass

    def exit(self, entity: "Player"):
        pass

    def update(self, entity: "Player", **kwargs):
        pass

    def can_transition(self, entity: "Player") -> Optional[str]:
        if not entity.grounded():
            return "jump"
        if entity.velocity.x != 0:
            return "run"
        return None


class IdleTurnState(State):
    def __init__(self):
        super().__init__("idleturn")

    def enter(self, entity: "Player"):
        pass

    def exit(self, entity: "Player"):
        pass

    def update(self, entity: "Player", **kwargs):
        pass

    def can_transition(self, entity: "Player") -> Optional[str]:
        if not entity.grounded():
            return "jump"
        if entity.velocity.x != 0:
            return "run"
        if entity.animation.has_animation_end():
            return "idle"
        return None


class JumpState(State):
    def __init__(self):
        super().__init__("jump")

    def enter(self, entity: "Player"):
        pass

    def exit(self, entity: "Player"):
        pass

    def update(self, entity: "Player", **kwargs):
        pass

    def can_transition(self, entity: "Player") -> Optional[str]:
        if entity.grounded():
            return "idle"
        if entity.velocity.y > 0:
            return "fall"
        slideable = getattr(entity, "can_slide", None)
        if slideable and slideable():
            return "wallslide"
        return None


class FallState(State):
    def __init__(self):
        super().__init__("fall")

    def enter(self, entity: "Player"):
        pass

    def exit(self, entity: "Player"):
        pass

    def update(self, entity: "Player", **kwargs):
        pass

    def can_transition(self, entity: "Player") -> Optional[str]:
        if entity.grounded():
            return "idle"
        slideable = getattr(entity, "can_slide", None)
        if slideable and slideable():
            return "wallslide"
        return None


class RunState(State):
    def __init__(self):
        super().__init__("run")

    def enter(self, entity: "Player"):
        pass

    def exit(self, entity: "Player"):
        pass

    def update(self, entity: "Player", **kwargs):
        pass

    def can_transition(self, entity: "Player") -> Optional[str]:
        if not entity.grounded():
            return "jump"
        if entity.velocity.x == 0:
            return "idle"
        return None


class SlideState(State):
    def __init__(self):
        super().__init__("wallslide")

    def enter(self, entity: "Player"):
        pass

    def update(self, entity: "Player", **kwargs):
        pass

    def can_transition(self, entity: "Player") -> Optional[str]:
        slideable = getattr(entity, "can_slide", None)
        if slideable and not slideable():
            return "jump" if not entity.grounded() else "idle"
        return None

    def exit(self, entity: "Player"):
        entity.flipped = not entity.flipped


class AttackState(State):
    def __init__(self):
        super().__init__("attack")

    def update(self, entity: "Player", **kwargs):
        pass

    def exit(self, entity: "Player"):
        pass

    def enter(self, entity: "Player"):
        entity.velocity.x = 0

    def can_transition(self, entity: "Player") -> Optional[str]:
        if entity.animation.has_animation_end():
            return "jump" if not entity.grounded() else "idle"
        return None


class HitState(State["Player"]):
    def __init__(self):
        super().__init__("hit")

    def enter(self, entity: "Player") -> None:
        entity.velocity *= 0
        entity.hit_timer.reset_to_now()

    def can_transition(self, entity: "Player"):
        if entity.animation.has_animation_end():
            if entity.grounded():
                return "idle"
            return "jump"
        return None
