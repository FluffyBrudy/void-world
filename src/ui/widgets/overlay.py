import math
from typing import List, Tuple, Unpack

from pygame import draw
from pygame.constants import SRCALPHA
from pygame.surface import Surface

from ttypes.index_type import UIOptions
from ui.base.uibase import UIBase
from utils.timer import Timer


class CooldownOverlay(UIBase):
    def __init__(self, progress_time: float, size: float | int, **overrides: Unpack[UIOptions]) -> None:
        super().__init__({"width": int(size), "height": int(size), **overrides})

        content_w, content_h = self.box_model["content_width"], self.box_model["content_height"]
        self.radius = min(content_w, content_h) // 2
        self.factor = 0.05
        self.overlay_parent = Surface((content_w, content_h), SRCALPHA)
        self.timer = Timer(progress_time, stale_init=True)
        self.is_active = True
        self.renderable_plugins.append(self.generate_overlay_surf)

    def active(self):
        self.is_active = True

    def inactive(self):
        self.is_active = False

    def reset(self):
        self.timer.reset_to_now()

    def generate_overlay_surf(self, surface: Surface):
        if not self.is_active:
            # will do something later
            return self.overlay_parent
        if self.timer.has_reached_interval():
            return self.overlay_parent

        center = (self.radius, self.radius)
        points: List[Tuple[int | float, int | float]] = [center]

        progress = 1 - self.timer.get_timediff_ratio()
        end_degress = int(progress * 360)
        for degree in range(-90, end_degress - 90):
            angle = math.radians(degree)
            x = self.radius + self.radius * math.cos(angle)
            y = self.radius + self.radius * math.sin(angle)
            points.append((x, y))

        op = self.overlay_parent
        op.fill((0, 0, 0, 0))
        if len(points) > 2:
            draw.polygon(op, (0, 0, 0, 100), points)

        pos = self.box_model["left"], self.box_model["top"]
        surface.blit(op, pos)

    def has_cooldown(self):
        return self.timer.has_reached_interval()

    def render(self, screen: Surface):
        super().render(screen)
