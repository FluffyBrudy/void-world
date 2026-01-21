from abc import ABC, abstractmethod
from math import cos, pi, sin
from random import randint, random, uniform
from typing import TYPE_CHECKING, Sequence, Tuple

from pygame import Surface, Vector2
from pygame.draw import circle as draw_circle
from pygame.typing import ColorLike

from constants import BASE_SPEED
from ttypes.index_type import TPosType

if TYPE_CHECKING:
    from particle_manager import ParticleManager


class Particle(ABC):
    @abstractmethod
    def update(self, dt: float) -> bool | None: ...

    @abstractmethod
    def render(self, surface: Surface, offset: Vector2 | Tuple[int, int]): ...


class DotParticle(Particle):
    def __init__(
        self,
        radius: int,
        pos: Tuple[int, int] | Vector2,
        velocity: Tuple[float, float] | Vector2 = (0, 0),
        color: ColorLike = (0, 0, 0, 255),
        filled: bool = False,
    ) -> None:
        self.ptype = "dot"
        self.radius = radius
        self.pos = Vector2(pos)
        self.velocity = Vector2(velocity)
        self.color = color
        self.fill_width = 0 if filled else 2

    def update(self, dt: float):
        self.pos.x += dt * BASE_SPEED * self.velocity.x
        self.pos.y += dt * BASE_SPEED * self.velocity.y
        self.radius = max(1, self.radius - 0.1)
        return self.radius == 1

    def render(self, surface: Surface, offset: Tuple[int, int] | Vector2):
        draw_circle(surface, self.color, self.pos - offset, self.radius, self.fill_width)


def coned_particles(
    pos: TPosType,
    base_angles: Sequence[float],
    group: "ParticleManager",
    filled=True,
    color=(0, 0, 0),
):
    for base_angle in base_angles:
        angle = base_angle
        if base_angle != 0:
            angle = base_angle + pi / 6 * (random() - 0.5)
        radius = randint(4, 8)
        speed = uniform(3, 5)
        velocity = cos(angle) * speed, sin(angle) * speed
        particle = DotParticle(
            radius,
            pos,
            velocity,
            color=color,
            filled=filled,
        )
        group.add(particle)
