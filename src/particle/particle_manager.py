from typing import TYPE_CHECKING, Set

from pygame import Surface

from particle.particles import Particle

if TYPE_CHECKING:
    from game import Game


class ParticleManager:
    game: "Game" = None  # type: ignore

    def __init__(self):
        self.particles: Set["Particle"] = set()

    def add(self, particle: Particle):
        self.particles.add(particle)

    def remove(self, particle: Particle):
        self.particles.remove(particle)

    def render(self, surface: Surface, dt: float):
        offset = ParticleManager.game.scroll
        new_particles = set()
        for particle in self.particles:
            if not particle.update(dt):
                particle.render(surface, offset)
                new_particles.add(particle)
        self.particles = new_particles
