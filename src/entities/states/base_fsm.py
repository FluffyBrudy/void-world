from typing import TYPE_CHECKING, Optional, TypeVar, Generic

if TYPE_CHECKING:
    from entities.physics_entity import PhysicsEntity

TEntity = TypeVar("TEntity", bound="PhysicsEntity")


class State(Generic[TEntity]):
    def __init__(self, name: str):
        self.name = name

    def enter(self, entity: TEntity) -> None:
        ...

    def exit(self, entity: TEntity) -> None:
        ...

    def update(self, entity: TEntity, **kwargs) -> None:
        ...

    def can_transition(self, entity: TEntity) -> Optional[str]:
        ...

    def __str__(self) -> str:
        return self.name
