from typing import TYPE_CHECKING, Unpack

import pygame
from pygame import Surface

from ttypes.index_type import UIOptions

from widgets.components.uibase import UIBase


if TYPE_CHECKING:
    from game import Game


HEALTH_BAR_DEFAULTS: UIOptions = {
    "width": 200,
    "height": 20,
    "border_width": 2,
    "border_radius": 5,
    "border_color": (50, 50, 50, 255),
    "background": (100, 30, 30, 255),
}


class SimpleHealthbarUI(UIBase):
    game: "Game" = None  # type: ignore

    def __init__(self, **overrides: Unpack[UIOptions]) -> None:
        options: UIOptions = {**HEALTH_BAR_DEFAULTS, **overrides}
        super().__init__(options)

        self.health_ratio = 1.0
        self.target_ratio = 1.0
        self.lerp_speed = 0.1

        self.fill_color = (0, 255, 100, 255)

    def set_health(self, current: float, maximum: float):
        self.health_ratio = max(0.0, min(1.0, current / maximum))

    def update(self):
        if self.health_ratio != self.target_ratio:
            diff = self.target_ratio - self.health_ratio
            self.health_ratio += diff * self.lerp_speed

            if abs(diff) <= 0.001:
                self.health_ratio = self.target_ratio

    def render(self, screen: Surface):
        self.draw_base()

        if self.health_ratio > 0:
            fill_width = int(self.box_model["content_width"] * self.health_ratio)

            inner_radius = max(0, self.border["radius"] - self.border["width"])

            pygame.draw.rect(
                self.local_surface,
                self.fill_color,
                (
                    self.box_model["left"],
                    self.box_model["top"],
                    fill_width,
                    self.box_model["content_height"],
                ),
                border_radius=inner_radius,
            )

        pos = (self.box_model["offset_x"], self.box_model["offset_y"])
        screen.blit(self.local_surface, pos)
