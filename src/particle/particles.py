from abc import ABC, abstractmethod
from math import cos, pi, radians, sin
from random import randint, random, uniform
from typing import TYPE_CHECKING, Sequence, Tuple

from pygame import Surface, Vector2
from pygame.constants import SRCALPHA
from pygame.draw import circle as draw_circle
from pygame.typing import ColorLike

from constants import BASE_SPEED
from pydebug import pgdebug
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


class TwinWave:
    reset_limit = pi * 50

    def __init__(
        self,
        start_pos: TPosType,
        radius: float,
        amplitude: float,
        wavelength: float,
        speed: float,
        color: Tuple[int, int, int],
        num_crossings: int,
    ):
        self.base_pos = Vector2(start_pos)
        self.radius = radius
        self.amplitude = amplitude
        self.wavelength = wavelength
        self.speed = speed
        self.num_crossings = num_crossings
        self.color = color[0:3]

        self.__omega = (2 * pi * self.speed) / self.wavelength
        self.__wavelength_junction = self.wavelength * 0.5
        self.__center = (self.amplitude, self.__wavelength_junction)
        self.time_tracker = 0

        self.__mask_surface = Surface((2 * self.amplitude + 2 * radius, self.wavelength + 2 * radius), SRCALPHA)

    def update(self, dt: float, current_center: TPosType):
        self.base_pos.update(current_center)
        self.time_tracker += self.__omega * dt
        if self.time_tracker > self.reset_limit:
            self.time_tracker = 0

    def render(self, surface: Surface, camera_offset: TPosType):
        self.__mask_surface.fill((0, 0, 0, 0))

        t = self.time_tracker
        angle_y = t
        angle_x = t * self.num_crossings

        off_x = sin(angle_x) * self.amplitude
        off_y = cos(angle_y) * self.__wavelength_junction

        alpha = int(abs(off_y) / self.__wavelength_junction * 255)
        color = (*self.color, alpha)

        masked_surf = self.__mask_surface
        mw, mh = masked_surf.size
        draw_circle(masked_surf, (color), (off_x + mw // 2, off_y + mh // 2), self.radius)
        draw_circle(masked_surf, (color), (-off_x + mw // 2, off_y + mh // 2), self.radius)
        surface.blit(masked_surf, (self.base_pos - self.__center) - camera_offset)


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
