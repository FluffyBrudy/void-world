import math
from typing import TYPE_CHECKING, Any, Callable, List, Optional, Tuple, Unpack

from pygame import draw, transform
from pygame.constants import SRCALPHA
from pygame.surface import Surface

from ttypes.index_type import UIOptions
from ui.base.uibase import UIBase
from managers.asset_manager import assets_manager

if TYPE_CHECKING:
    from game import Game
    from lib.skill import Skill


class CooldownOverlay(UIBase):
    game: "Game" = None  # type: ignore

    def __init__(
        self,
        skill: "Skill",
        size: int | float,
        icon: Optional[Surface] = None,
        **overrides: Unpack[UIOptions],
    ) -> None:
        super().__init__({"width": int(size), "height": int(size), **overrides})

        self.skill = skill
        self.timer = skill.cooldown_timer

        content_w = self.box_model["content_width"]
        content_h = self.box_model["content_height"]

        r = min(content_w, content_h) / 2
        self.radius = r
        self.scalar = 1.0
        b = overrides.get("border_radius", 0)
        if b < r:
            self.scalar = 1.0
            self.scalar = (math.sqrt(2 * (r - b) ** 2) + b) / r

        self.overlay_parent = Surface((content_w, content_h), SRCALPHA)
        self.add_plugin(self.generate_overlay_surf)
        self.add_plugin(self.display_icon)

        if isinstance(icon, Surface):
            scale = content_w / icon.width, content_h / icon.height
            self.icon = transform.scale_by(icon, scale)

    def display_icon(self, surface: Surface):
        icon: Surface | None = getattr(self, "icon", None)
        if icon is None:
            return

        center_x = self.box_model["content_width"] // 2
        center_y = self.box_model["content_height"] // 2

        rect = icon.get_rect(center=(self.box_model["left"] + center_x, self.box_model["top"] + center_y))

        if not self.timer.has_reached_interval():
            icon.set_alpha(150)
        elif icon.get_alpha() != 255:
            icon.set_alpha(255)
        surface.blit(icon, rect.topleft)

    def generate_overlay_surf(self, surface: Surface):
        cross_intrvl = self.timer.has_reached_interval()

        if cross_intrvl:
            return self.overlay_parent

        ratio = self.timer.get_timediff_ratio()
        progress = 1.0 - ratio

        center = (self.radius, self.radius)
        points: List[Tuple[float, float]] = [center]

        end_degrees = int(progress * 360)

        for degree in range(-90, end_degrees - 90):
            angle = math.radians(degree)
            x = self.radius + self.radius * math.cos(angle) * self.scalar
            y = self.radius + self.radius * math.sin(angle) * self.scalar
            points.append((x, y))

        op = self.overlay_parent
        op.fill((0, 0, 0, 0))

        if len(points) > 2:
            draw.polygon(op, (0, 0, 0, 255), points)

        remaining_ms = self.timer.get_timediff_ratio()
        remaining_sec = round(1 - remaining_ms, 1)

        label = assets_manager.fonts["monogram"].render(
            str(remaining_sec),
            True,
            (255, 255, 255),
        )

        label_pos = (
            (surface.get_width() - label.get_width()) // 2,
            (surface.get_height() - label.get_height()) // 2,
        )

        pos = self.box_model["left"], self.box_model["top"]
        surface.blit(op, pos)
        surface.blit(label, label_pos)
