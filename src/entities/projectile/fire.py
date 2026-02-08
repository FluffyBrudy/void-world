from typing import List

from pygame import Rect, Surface
from pygame.math import Vector2

from constants import BASE_SPEED
from managers.asset_manager import assets_manager
from ttypes.index_type import TPosType


class FireProjectile:
    __instances: List["FireProjectile"] = []

    def __init__(self, start_pos: TPosType, velocity: TPosType, projectile_range: float, flipped=False) -> None:
        self.velocity = Vector2(velocity)
        self.projectile_range = projectile_range
        self.animation = assets_manager.assets["projectile/fire"].copy()
        self.pos = Vector2(start_pos)
        self.size = self.animation.get_frame().size

        self.ready_to_kill = False

        FireProjectile.__instances.append(self)

    def rect(self):
        return Rect(*(self.pos[0], self.pos[1]), *self.size)

    def update(self, dt: float):
        self.animation.update()

        displacement = self.velocity * dt * BASE_SPEED
        self.pos += displacement
        self.projectile_range -= displacement.magnitude()
        if self.projectile_range <= 0 and not self.ready_to_kill:
            self.mark_ready_to_kill()
        return self.ready_to_kill and self.animation.has_animation_end()

    def mark_ready_to_kill(self):
        """WARNING: do not call this if ready_to_kill is True"""
        self.ready_to_kill = True
        self.animation = assets_manager.assets["projectile/fire_explosion"].copy()
        self.velocity = Vector2(0, 0)

    def render(self, surface: Surface, offset: Vector2):
        frame = self.animation.get_frame()
        surface.blit(frame, self.pos - offset)

    @classmethod
    def get_instances(cls):
        """
        INFO: filtering is required otherwise if any collision checks use
        original instances they refresh animation on each frame which
        keeps projectile alive forever with stucked animation
        """
        return [x for x in cls.__instances if not x.ready_to_kill]

    @classmethod
    def render_all(cls, surface: Surface, dt: float, offset: Vector2):
        alive = []
        for instance in cls.__instances:
            if not instance.update(dt):
                alive.append(instance)
                instance.render(surface, offset)
        cls.__instances = alive
