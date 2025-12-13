from pathlib import Path
from typing import TYPE_CHECKING, Dict, List, Set, Tuple, cast
from pygame import Rect, Surface, Vector2
import pygame
from pytmx import TiledMap, TiledObjectGroup, TiledTileLayer, TiledTileset, load_pygame
from lib.tile import Tile
from constants import (
    GRID_NEIGHBOURS_9,
    MAP_PATH,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
)


if TYPE_CHECKING:
    from game import Game


AVOIDABLE_TILESETS = ("marker",)


class Tilemap:
    game: "Game" = None  # type: ignore

    def __init__(self, **kwargs) -> None:
        self.tile_scale = kwargs.get("tile_scale", 1)
        self.grid_tiles: Dict[Tuple[int, int], "Tile"] = {}
        self.grid_nocollision_tiles: Dict[Tuple[int, int], "Tile"] = {}

        self.tile_cache: Dict[int, Surface] = {}
        self.object_cache: Dict[int, Surface] = {}

        self.load_map(getattr(self.game, "level", 0))

    def physics_tiles_around(self, grid_pos: Tuple[int, int]) -> List[Tuple[int, int]]:
        tiles: List = []
        gx, gy = grid_pos

        for nx, ny in GRID_NEIGHBOURS_9:
            new_x, new_y = gx + nx, gy + ny
            tile_loc = (new_x, new_y)
            if (
                tile_loc in self.grid_tiles
                and tile_loc not in self.grid_nocollision_tiles
            ):
                tiles.append(tile_loc)

        return tiles

    def physics_rect_around(
        self, pos: Tuple[float | int, float | int] | Vector2
    ) -> List[Rect]:
        rects = []

        tw, th = self.tilewidth, self.tileheight
        grid_x = int(pos[0] // self.tilewidth)
        grid_y = int(pos[1] // self.tileheight)

        for tile_x, tile_y in self.physics_tiles_around((grid_x, grid_y)):
            rect = pygame.Rect(tile_x * tw, tile_y * th, tw, th)
            rects.append(rect)
        return rects

    def load_map(self, map_id: int):
        map_path = MAP_PATH / f"{map_id}.tmx"
        try:
            map_data = load_pygame(str(map_path))
            self.tilewidth = int(map_data.tilewidth * self.tile_scale)
            self.tileheight = int(map_data.tileheight * self.tile_scale)

            for layer in map_data.layers:
                if isinstance(layer, TiledTileLayer):
                    self.__load_tile_layer(layer, map_data)
                elif isinstance(layer, TiledObjectGroup):
                    self.__load_object_layer(layer, map_data)
            return True
        except Exception as e:
            print(e)
            return False

    def __load_tile_layer(self, layer: "TiledTileLayer", map_data: "TiledMap"):
        for x, y, surf in layer.tiles():
            gid = layer.data[y][x]
            if gid not in self.tile_cache:
                self.tile_cache[gid] = pygame.transform.scale_by(surf, self.tile_scale)
            tile = Tile(gid, (x * self.tilewidth, y * self.tileheight))
            props = map_data.get_tile_properties_by_gid(gid)
            if props is not None and props.get("no_collision"):
                self.grid_nocollision_tiles[(x, y)] = tile
            else:
                self.grid_tiles[(x, y)] = tile

    def __load_object_layer(self, layer: "TiledObjectGroup", map_data: "TiledMap"):
        for _ in layer:
            pass  # later

    def render(self):
        surface = self.game.screen
        scroll = self.game.scroll

        start_x = int(scroll.x // self.tilewidth)
        end_x = int(start_x + (SCREEN_WIDTH // self.tilewidth))
        start_y = int(scroll.y // self.tileheight)
        end_y = int(start_y + (SCREEN_HEIGHT // self.tileheight))
        for y in range(start_y, end_y + 2):
            for x in range(start_x, end_x + 2):
                location = (x, y)
                if location in self.grid_tiles:
                    tile = self.grid_tiles[location]
                    pos = tile.pos - scroll
                    surf = self.tile_cache[tile.tile_id]
                    surface.blit(surf, pos)
                if location in self.grid_nocollision_tiles:
                    tile = self.grid_nocollision_tiles[location]
                    pos = tile.pos - scroll
                    surf = self.tile_cache[tile.tile_id]
                    surface.blit(surf, pos)
