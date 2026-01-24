from typing import TYPE_CHECKING, Generic, Optional, TypeVar

if TYPE_CHECKING:
    from entities.base_entity import BaseEntity

TEntity = TypeVar("TEntity", bound="BaseEntity")


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
