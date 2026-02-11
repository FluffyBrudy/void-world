from typing import TYPE_CHECKING, Optional

from entities.states.base_fsm import State

if TYPE_CHECKING:
    from entities.player import Player


class IdleState(State["Player"]):
    def __init__(self, startup_frame=0, active_frame=0):
        super().__init__("idle", startup_frame, active_frame)

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


class IdleTurnState(State["Player"]):
    def __init__(self, startup_frame=0, active_frame=0):
        super().__init__("idleturn", startup_frame, active_frame)

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


class JumpState(State["Player"]):
    def __init__(self, startup_frame=0, active_frame=0):
        super().__init__("jump", startup_frame, active_frame)

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


class FallState(State["Player"]):
    def __init__(self, loop=True, startup_frame=0, active_frame=0):
        super().__init__("fall", startup_frame, active_frame)
        self.loop = loop

    def enter(self, entity: "Player"):
        entity.animation.loop = False

    def exit(self, entity: "Player"):
        pass

    def update(self, entity: "Player", **kwargs):
        if entity.animation.has_animation_end() and entity.animation.name == "player/fall":
            entity.set_animation("player/fall_loop")
            entity.animation.loop = self.loop

    def can_transition(self, entity: "Player") -> Optional[str]:
        if entity.grounded():
            return "idle"
        slideable = getattr(entity, "can_slide", None)
        if slideable and slideable():
            return "wallslide"
        return None


class RunState(State["Player"]):
    def __init__(self, startup_frame=0, active_frame=0):
        super().__init__("run", startup_frame, active_frame)

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


class SlideState(State["Player"]):
    def __init__(self, startup_frame=0, active_frame=0):
        super().__init__("wallslide", startup_frame, active_frame)

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


class AttackState(State["Player"]):
    def __init__(self, startup_frame=0, active_frame=0):
        super().__init__("attack", startup_frame, active_frame)

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
    def __init__(self, startup_frame=0, active_frame=0):
        super().__init__("hit", startup_frame, active_frame)

    def enter(self, entity: "Player") -> None:
        entity.velocity *= 0
        entity.hit_timer.reset_to_now()

    def can_transition(self, entity: "Player"):
        if entity.animation.has_animation_end():
            if entity.grounded():
                return "idle"
            return "jump"
        return None


class SkillCastState(State["Player"]):
    def __init__(self, loop=False, startup_frame=0, active_frame=0):
        super().__init__("skillcast", startup_frame, active_frame)
        self.loop = loop

    def update(self, entity: "Player", **kwargs) -> None:
        entity.velocity.x *= 0
        entity.velocity.y -= 0.1

    def can_transition(self, entity: "Player") -> Optional[str]:
        if entity.animation.has_animation_end():
            if entity.grounded():
                return "idle"
            return "jump"
        return None
