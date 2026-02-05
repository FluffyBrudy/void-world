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
from pygame.surface import Surface

from entities.states.base_fsm import State
from ttypes.index_type import TPosType
from utils.animation import Animation

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
    states: Dict[str, State]
    stats: Dict[str, float]
    current_state: State
    offset: Tuple[int, int]
    animation: "Animation"

    def __init__(
        self,
        etype: str,
        pos: Tuple[int, int],
        size: Tuple[int, int],
        states: Dict[str, State],
        offset: Tuple[int, int] = (0, 0),
    ):
        if etype not in AUTO_ADD_AVOIDABLES:
            BaseEntity.add_to_group(self)

        self.etype = etype
        self.pos = pygame.Vector2(pos)
        self.size = size
        self.flipped = False
        self.states = states
        self.offset = offset

        default_state = "idle" if "idle" in self.states else list(self.states.keys())[0]
        self.current_state = self.states[default_state]
        self.animation = self.game.assets[etype + "/" + self.current_state.name]

        self.stats = {"health": 1.0, "mana": float("-inf")}

        self.alive = True

    def rect(self):
        return pygame.Rect(self.pos, self.animation.get_frame().size)

    def hitbox(self) -> pygame.Rect:
        x, y = self.pos
        ox, oy = self.offset
        new_w, new_h = self.size[0] - 2 * ox, self.size[1] - 2 * oy
        new_y = oy + y
        new_x = x + ox
        return pygame.Rect(new_x, new_y, new_w, new_h)

    @abstractmethod
    def grounded(self) -> bool: ...

    def modify_stat(self, stat_name: str, value: float): ...

    def set_state(self, new_state: str):
        if self.current_state and new_state != self.current_state.name:
            self.current_state = self.states[new_state]
            self.animation = self.game.assets[self.etype + "/" + new_state].copy()

    def get_state(self) -> str:
        return self.current_state.name if self.current_state else ""

    def transition_to(self, new_state: str):
        if self.current_state:
            self.current_state.exit(self)
            self.set_state(new_state)
            self.current_state.enter(self)

    def manage_state(self):
        if self.current_state:
            next_state = self.current_state.can_transition(self)
            if next_state is not None:
                self.transition_to(next_state)
            self.current_state.update(self)

    @abstractmethod
    def handle_movement(self, dt: float): ...

    def update(self, dt: float):
        self.manage_state()
        if self.animation:
            self.animation.update()

    def get_renderable(self, offset: TPosType):
        frame = self.animation.get_frame()
        render_pos = self.pos - pygame.Vector2(offset)

        if self.flipped:
            frame = pygame.transform.flip(frame, True, False)

        render_pos.x += (self.size[0] - frame.get_width()) / 2
        render_pos.y += (self.size[1] - frame.get_height()) / 2

        return frame, render_pos

    def remove(self):
        cls = type(self)
        BaseEntity.__instances.remove(self)
        BaseEntity.__registry[cls].remove(self)

    def render(self, surface: pygame.Surface, offset: TPosType):
        frame, render_pos = self.get_renderable(offset)
        surface.blit(frame, render_pos)

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
    def render_all(cls, screen: Surface, dt: float, offset: TPosType):
        killable: Set["BaseEntity"] = set()
        for entity in cls.__instances:
            if entity.alive:
                entity.update(dt)
                entity.render(screen, offset)
            else:
                killable.add(entity)

        if len(killable) > 0:
            for entity in killable:
                entity.remove()

    def get_visual_correction(self):
        return (0.0, 0.0)
