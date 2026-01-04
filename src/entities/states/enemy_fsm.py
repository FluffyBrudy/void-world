from typing import TYPE_CHECKING, Optional
from entities.states.base_fsm import State

if TYPE_CHECKING:
    from entities.physics_entity import PhysicsEntity


class FlyState(State):
    def __init__(self):
        super().__init__("fly")

    def enter(self, entity: "PhysicsEntity"):
        pass

    def can_transition(self, entity: "PhysicsEntity") -> Optional[str]:
        pass

    def update(self, entity: "PhysicsEntity", **kwargs):
        pass

    def exit(self, entity: "PhysicsEntity"):
        pass


class Attack(State):
    def __init__(self):
        super().__init__("attack")

    def enter(self, entity: "PhysicsEntity"):
        pass

    def can_transition(self, entity: "PhysicsEntity") -> Optional[str]:
        pass

    def update(self, entity: "PhysicsEntity", **kwargs):
        pass

    def exit(self, entity: "PhysicsEntity"):
        pass


class Hit(State):
    def __init__(self):
        super().__init__("hit")

    def enter(self, entity: "PhysicsEntity"):
        pass

    def can_transition(self, entity: "PhysicsEntity") -> Optional[str]:
        pass

    def update(self, entity: "PhysicsEntity", **kwargs):
        pass

    def exit(self, entity: "PhysicsEntity"):
        pass
