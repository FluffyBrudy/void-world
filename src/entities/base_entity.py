from abc import ABC, abstractmethod
from typing import (
    TYPE_CHECKING,
    Dict,
    Set,
    Tuple,
    Type,
    TypeVar,
    cast,
)
import pygame


if TYPE_CHECKING:
    from game import Game


TEntity = TypeVar("TEntity", bound="BaseEntity")


AUTO_ADD_AVOIDABLES = ("player",)


class BaseEntity(ABC):
    game: "Game" = None  # type: ignore
    __instances: Set["BaseEntity"] = set()
    __registry: Dict[Type["BaseEntity"], Set["BaseEntity"]] = {}

    etype: str
    pos: pygame.Vector2
    size: Tuple[int, int]
    flipped: bool

    def __init__(self, etype: str, pos: Tuple[int, int], size: Tuple[int, int]):
        if etype not in AUTO_ADD_AVOIDABLES:
            BaseEntity.add_to_group(self)

        self.etype = etype
        self.pos = pygame.Vector2(pos)
        self.size = size
        self.flipped = False

    @abstractmethod
    def hitbox(self) -> pygame.Rect:
        ...

    @abstractmethod
    def grounded(self) -> bool:
        ...

    @abstractmethod
    def set_state(self, new_state: str):
        ...

    @abstractmethod
    def get_state(self) -> str:
        ...

    @abstractmethod
    def manage_state(self):
        ...

    @abstractmethod
    def handle_movement(self, dt: float):
        ...

    @abstractmethod
    def update(self, dt: float):
        ...

    @abstractmethod
    def render(self, surface: pygame.Surface):
        ...

    @classmethod
    def add(cls: Type[TEntity], instance: TEntity):
        """maybe shouldnt use this externally, just for convinience its here"""
        cls.__instances.add(instance)

    @classmethod
    def add_to_group(cls: Type[TEntity], entity: TEntity):
        """maybe shouldnt use this externally, just for convinience its here"""
        registry_key = type(entity)

        if registry_key not in BaseEntity.__registry:
            BaseEntity.__registry[registry_key] = set()
        BaseEntity.__registry[registry_key].add(entity)
        BaseEntity.__instances.add(entity)

    @classmethod
    def get_by_group(cls: Type[TEntity]) -> Set[TEntity]:
        return cast(Set[TEntity], BaseEntity.__registry.get(cls, set()))

    @classmethod
    def remove(cls: Type[TEntity], instance: TEntity):
        cls.__instances.remove(instance)

    @classmethod
    def render_all(cls, dt: float):
        surface = cls.game.screen
        for bat in cls.__instances:
            bat.update(dt)
            bat.render(surface)
