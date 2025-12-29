from typing import Tuple
import pygame
from pygame.typing import IntPoint


AREA_TILE_BORDER_COLOR = (39, 59, 58, 255)
AREA_TILE_COLOR = (59, 137, 135, 255)


class Tile:
    def __init__(self, tile_id: int, pos: Tuple[int, int]) -> None:
        self.tile_id = tile_id
        self.pos = pos


# class AreaTile:
#     __slots__ = ("surface", "rect")

#     def __init__(
#         self,
#         pos: IntPoint,
#         size: IntPoint,
#         tile_color: pygame.typing.ColorLike = AREA_TILE_COLOR,
#         border_color: pygame.typing.ColorLike = AREA_TILE_COLOR,
#         border_size: int = 2,
#         border_radius: int = 2,
#     ) -> None:
#         self.rect = pygame.Rect(pos, size)
#         self.surface = pygame.Surface(size, pygame.SRCALPHA)
#         self.surface.fill(tile_color)
#         pygame.draw.rect(
#             self.surface,
#             border_color,
#             self.surface.get_rect(),
#             border_size,
#             border_radius,
#         )
