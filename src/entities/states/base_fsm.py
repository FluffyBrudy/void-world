from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from entities.physics_entity import PhysicsEntity


class State(ABC):
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def enter(self, entity: "PhysicsEntity"):
        ...

    @abstractmethod
    def exit(self, entity: "PhysicsEntity"):
        ...

    @abstractmethod
    def update(self, entity: "PhysicsEntity", **kwargs):
        """for future" maybe if i feel i need"""
        ...

    @abstractmethod
    def can_transition(self, entity: "PhysicsEntity") -> Optional[str]:
        ...

    def __str__(self) -> str:
        return self.name
