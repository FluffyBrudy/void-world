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
    def __init__(
        self,
        pos: TPosType,
        ptype: str,
        velocity: Tuple[float, float] | Vector2 = (0, 0),
        color: ColorLike = (0, 0, 0, 255),
    ) -> None:
        self.ptype = ptype
        self.pos = Vector2(pos)
        self.velocity = Vector2(velocity)
        self.color = color

    @abstractmethod
    def update(self, dt: float) -> bool | None: ...

    @abstractmethod
    def render(self, surface: Surface, offset: Vector2 | Tuple[int, int]): ...


class DotParticle(Particle):
    def __init__(
        self,
        radius: float,
        pos: TPosType,
        velocity: Tuple[float, float] | Vector2 = (0, 0),
        reduce_factor: float = 0.1,
        color: ColorLike = (0, 0, 0, 255),
        filled: bool = False,
    ) -> None:
        super().__init__(pos, "dot", velocity, color)
        self.radius = radius
        self.fill_width = 0 if filled else 2
        self.reduce_factor = reduce_factor

    def update(self, dt: float):
        self.pos.x += dt * BASE_SPEED * self.velocity.x
        self.pos.y += dt * BASE_SPEED * self.velocity.y
        self.radius = max(1, self.radius - self.reduce_factor)
        return self.radius <= 1

    def render(self, surface: Surface, offset: Tuple[int, int] | Vector2):
        draw_circle(surface, self.color, self.pos - offset, self.radius, self.fill_width)


def coned_particles(
    pos: TPosType,
    base_angles: Sequence[float],
    group: "ParticleManager",
    filled: bool,
    color: ColorLike,
    radius: float,
    speed_range: tuple[float, float],
    reduce_factor: float,
):
    for base_angle in base_angles:
        angle = base_angle
        if base_angle != 0:
            angle += (pi / 6) * (random() - 0.5)

        spawn_dot_particle(
            group=group,
            pos=pos,
            radius=radius,
            angle=angle,
            speed_range=speed_range,
            reduce_factor=reduce_factor,
            color=color,
            filled=filled,
        )


def radial_particles(
    pos: TPosType,
    group: "ParticleManager",
    filled: bool,
    color: ColorLike,
    radius_range: tuple[int, int],
    speed_range: tuple[float, float],
    reduce_factor: float,
    count: int = 12,
):
    full_angle = 2 * pi
    step = full_angle / count
    angle = 0.0

    while angle < full_angle:
        radius = randint(*radius_range)

        spawn_dot_particle(
            group=group,
            pos=pos,
            radius=radius,
            angle=angle,
            speed_range=speed_range,
            reduce_factor=reduce_factor,
            color=color,
            filled=filled,
        )

        angle += step


def spawn_dot_particle(
    group: "ParticleManager",
    pos: TPosType,
    radius: float,
    angle: float,
    speed_range: tuple[float, float],
    reduce_factor: float,
    color: ColorLike,
    filled: bool,
) -> DotParticle:
    speed = uniform(*speed_range)
    velocity = (cos(angle) * speed, sin(angle) * speed)

    particle = DotParticle(
        radius=radius,
        pos=pos,
        velocity=velocity,
        reduce_factor=reduce_factor,
        color=color,
        filled=filled,
    )

    group.add(particle)
    return particle
