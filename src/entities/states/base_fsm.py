from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from entities.physics_entity import PhysicsEntity


class State:
    def __init__(self, name: str):
        self.name = name

    def enter(self, entity: "PhysicsEntity"):
        ...

    def exit(self, entity: "PhysicsEntity"):
        ...

    def update(self, entity: "PhysicsEntity", **kwargs):
        """for future" maybe if i feel i need"""
        ...

    def can_transition(self, entity: "PhysicsEntity") -> Optional[str]:
        ...

    def __str__(self) -> str:
        return self.name
