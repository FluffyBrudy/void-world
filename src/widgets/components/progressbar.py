from typing import TYPE_CHECKING, Unpack, cast

import pygame
from pygame import Surface

from ttypes.index_type import UIOptions

from utils.interpolation import SimpleInterpolation
from widgets.components.uibase import UIBase


if TYPE_CHECKING:
    from game import Game


PROGRESSBAR_DEFAULTS = cast(
    UIOptions,
    {
        "width": 250,
        "height": 24,
        "border_width": 2,
        "border_radius": 6,
        "padding_x": 2,
        "padding_y": 2,
        "margin_x": 0,
        "margin_y": 0,
        "border_color": (40, 44, 52, 255),
        "background": (33, 37, 43, 255),
        "fill_color": (255, 255, 255, 255),
    },
)


class ProgressBarUI(UIBase):
    game: "Game" = None  # type: ignore

    def __init__(self, **overrides: Unpack[UIOptions]) -> None:
        options: UIOptions = {**PROGRESSBAR_DEFAULTS, **overrides}
        super().__init__(options)
        self.colors["fill"] = options.get("fill_color", (255, 255, 255, 255))

        self.interpolation = SimpleInterpolation(speed=0.05)

    def set_progress(self, value: float):
        self.interpolation.set(value)

    def get_progress(self):
        return self.interpolation.current * self.box_model["content_width"]

    def update(self):
        self.interpolation.update()

    def render(self, screen: Surface, pos_offset=(0, 0)):
        self.draw_base()

        intrp_current = self.interpolation.current
        if intrp_current > 0:
            fill_width = int(self.box_model["content_width"] * intrp_current)
            inner_radius = max(0, self.border["radius"] - self.border["width"])

            pygame.draw.rect(
                self.local_surface,
                self.colors["fill"],
                (
                    self.box_model["left"],
                    self.box_model["top"],
                    fill_width,
                    self.box_model["content_height"],
                ),
                border_radius=inner_radius,
            )

        pos_offset_x, pos_offset_y = pos_offset
        pos = (
            self.box_model["offset_x"] + pos_offset_x,
            self.box_model["offset_y"] + pos_offset_y,
        )
        screen.blit(self.local_surface, pos)
