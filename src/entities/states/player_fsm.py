from typing import TYPE_CHECKING, List, Callable, Optional

if TYPE_CHECKING:
    from entities.physics_entity import PhysicsEntity


class State:
    def __init__(self, name: str):
        self.name = name

    def enter(self, entity: "PhysicsEntity"):
        pass

    def exit(self, entity: "PhysicsEntity"):
        pass

    def update(self, entity: "PhysicsEntity", dt: float):
        """for future" maybe if i feel i need"""
        pass

    def can_transition(self, entity: "PhysicsEntity") -> Optional[str]:
        return None

    def __str__(self) -> str:
        return self.name


class IdleState(State):
    def __init__(self):
        super().__init__("idle")

    def can_transition(self, entity: "PhysicsEntity"):
        if not entity.grounded():
            return "jump"
        if entity.velocity.x != 0:
            return "run"
        return None


class IdleTurnState(State):
    def __init__(self):
        super().__init__("idleturn")

    def can_transition(self, entity: "PhysicsEntity"):
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

    def can_transition(self, entity: "PhysicsEntity"):
        if entity.grounded():
            return "idle"
        elif entity.velocity.y > 0:
            return "fall"
        slideable = getattr(entity, "can_slide")
        if slideable and slideable():
            return "wallslide"

        return None


class FallState(State):
    def __init__(self):
        super().__init__("fall")

    def can_transition(self, entity: "PhysicsEntity"):
        if entity.grounded():
            return "idle"
        slideable = getattr(entity, "can_slide")
        if slideable and slideable():
            return "wallslide"

        return None


class RunState(State):
    def __init__(self):
        super().__init__("run")

    def can_transition(self, entity: "PhysicsEntity"):
        if not entity.grounded():
            return "jump"
        if entity.velocity.x == 0:
            return "idle"

        return None


class SlideState(State):
    def __init__(self):
        super().__init__("wallslide")

    def can_transition(self, entity: "PhysicsEntity"):
        slideable = getattr(entity, "can_slide")
        if slideable and not slideable():
            return "jump" if not entity.grounded() else "idle"
        return None

    def exit(self, entity: "PhysicsEntity"):
        entity.flipped = not entity.flipped


class AttackState(State):
    def __init__(self):
        super().__init__("attack")

    def enter(self, entity: "PhysicsEntity"):
        entity.velocity.x = 0

    def can_transition(self, entity: "PhysicsEntity") -> Optional[str]:
        if entity.animation.has_animation_end():
            if not entity.grounded():
                return "jump"
            return "idle"
        return None
