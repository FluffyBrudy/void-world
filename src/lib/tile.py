from typing import Tuple


AREA_TILE_BORDER_COLOR = (39, 59, 58, 255)
AREA_TILE_COLOR = (59, 137, 135, 255)


class Tile:
    def __init__(self, tile_id: int, pos: Tuple[int, int]) -> None:
        self.tile_id = tile_id
        self.pos = pos
