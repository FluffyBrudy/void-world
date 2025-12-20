from typing import TYPE_CHECKING, List, Callable, Optional

if TYPE_CHECKING:
    from entities.physics_entity import PhysicsEntity


class State:
    def __init__(self, name: str):
        self.name = name

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
        if not entity.is_grounded():
            return "jump"
        if entity.velocity.x != 0:
            return "run"
        if entity.can_slide():
            return "slide"
        return None


class JumpState(State):
    def __init__(self):
        super().__init__("jump")

    def can_transition(self, entity: "PhysicsEntity"):
        if entity.is_grounded():
            return "idle"
        return None


class RunState(State):
    def __init__(self):
        super().__init__("run")

    def can_transition(self, entity: "PhysicsEntity"):
        if not entity.is_grounded():
            return "jump"
        if entity.velocity.x == 0:
            return "idle"
        if entity.can_slide():
            return "slide"
        return None


class SlideState(State):
    def __init__(self):
        super().__init__("slide")

    def can_transition(self, entity: "PhysicsEntity"):
        if not entity.can_slide():
            return "jump" if not entity.is_grounded() else "idle"
        return None
