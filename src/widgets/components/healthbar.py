from typing import TYPE_CHECKING, Unpack

from pygame import SRCALPHA, Surface
import pygame

from ttypes.index_type import UIOptions
from utils.style_utils import generate_box_model


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


class UIBase:
    game: "Game" = None  # type: ignore

    def __init__(self, options: UIOptions) -> None:
        self.colors = {"bg": options.get("background", (0, 0, 0, 0))}

        self.box_model = generate_box_model(options)

        self.border = {
            "radius": options.get("border_radius", 0),
            "width": options.get("border_width", 0),
            "color": options.get("border_color", (0, 0, 0, 0)),
        }

        local_size = self.box_model["full_width"], self.box_model["full_height"]
        self.local_surface = Surface(local_size, SRCALPHA)

    def draw_base(self):
        local_surf = self.local_surface
        local_surf.fill((0, 0, 0, 0))

        bg_color = self.colors["bg"]
        border_width = self.border["width"]
        border_radius = self.border["radius"]
        border_color = self.border["color"]

        content_pos = self.box_model["left"], self.box_model["top"]
        content_size = self.box_model["content_width"], self.box_model["content_height"]
        surface_size = local_surf.get_size()

        if border_width > 0:
            pygame.draw.rect(
                local_surf,
                border_color,
                (0, 0, *surface_size),
                width=border_width,
                border_radius=border_radius,
            )

        pygame.draw.rect(
            local_surf,
            bg_color,
            (*content_pos, *content_size),
            border_radius=max(0, border_radius - border_width),
        )

    def render(self, screen: Surface):
        self.draw_base()
        pos = (self.box_model["offset_x"], self.box_model["offset_y"])
        screen.blit(self.local_surface, pos)


class SimpleHealthbarUI(UIBase):
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
