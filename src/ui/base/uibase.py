import pygame
from pygame import SRCALPHA, Surface

from ttypes.index_type import UIOptions
from utils.style_utils import generate_box_model


class UIBase:
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

    @property
    def fullsize(self):
        return (self.box_model["full_width"], self.box_model["full_height"])

    def render(self, screen: Surface):
        self.draw_base()
        pos = (self.box_model["offset_x"], self.box_model["offset_y"])
        screen.blit(self.local_surface, pos)
