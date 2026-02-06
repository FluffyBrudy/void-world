from pathlib import Path
from typing import TYPE_CHECKING, Dict, List, Sequence, Set, Tuple, TypedDict, cast

import pygame
from pygame import Rect, Surface, Vector2
from pygame.typing import IntPoint
from pytmx import TiledMap, TiledObjectGroup, TiledTileLayer, TiledTileset, load_pygame

from constants import (
    GRID_NEIGHBOURS_9,
    MAP_PATH,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
)
from lib.tile import Tile

if TYPE_CHECKING:
    from game import Game


AVOIDABLE_TILESETS = ("marker",)


class TileProps(TypedDict, total=True):
    inflate: Rect


class Tilemap:
    game: "Game" = None  # type: ignore

    def __init__(self, **kwargs) -> None:
        self.tile_props: Dict[int, TileProps] = {}

        self.tile_scale = kwargs.get("tile_scale", 1)
        self.grid_tiles: Dict[Tuple[int, int], "Tile"] = {}
        self.grid_optional_collision_tiles: Dict[Tuple[int, int], "Tile"] = {}

        self.tile_cache: Dict[int, Surface] = {}
        self.object_cache: Dict[int, Surface] = {}

        self.load_map(getattr(self.game, "level", 0))

    def get_physics_rects(self, area: Rect) -> List[Rect]:
        rects: List[Rect] = []
        tw, th = self.tilewidth, self.tileheight

        start_x = int(area.left // tw) - 1
        end_x = int(area.right // tw) + 1
        start_y = int(area.top // th) - 1
        end_y = int(area.bottom // th) + 1

        for y in range(start_y, end_y + 1):
            for x in range(start_x, end_x + 1):
                if (x, y) in self.grid_tiles:
                    rects.append(pygame.Rect(x * tw, y * th, tw, th))
        return rects

    def is_solid_tile(self, pos: IntPoint):
        x = int(pos[0] // self.tilewidth)
        y = int(pos[1] // self.tileheight)
        return (x, y) in self.grid_tiles

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
                if gid not in self.tile_props:
                    cached_surf = self.tile_cache[gid]
                    self.tile_props[gid] = {"inflate": cached_surf.get_bounding_rect()}
                self.grid_optional_collision_tiles[(x, y)] = tile
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
                if location in self.grid_optional_collision_tiles:
                    tile = self.grid_optional_collision_tiles[location]
                    pos = tile.pos - scroll
                    surf = self.tile_cache[tile.tile_id]
                    surface.blit(surf, pos)
