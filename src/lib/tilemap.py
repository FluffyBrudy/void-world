from pathlib import Path
from typing import TYPE_CHECKING, Dict, List, Tuple, cast
from pygame import Surface
from pytmx import TiledMap, TiledObjectGroup, TiledTileLayer, TiledTileset, load_pygame
from lib.tile import Tile
from constants import (
    ASSETS_PATH,
    GRID_NEIGHBOURS_9,
    MAP_PATH,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
)
from utils.image_utils import load_image


if TYPE_CHECKING:
    from game import Game


AVOIDABLE_TILESETS = ("marker",)


class Tilemap:
    game: "Game" = None  # type: ignore

    def __init__(self) -> None:
        self.grid_tiles: Dict[Tuple[int, int], "Tile"] = {}
        self.offgrid: List["Tile"] = []

        self.tileset_cache: Dict[int, Surface] = {}
        self.object_cache: Dict[int, Surface] = {}

        self.load_map(getattr(self.game, "level", 0))

    def physics_tiles_around(self, pos: Tuple[int, int]):
        tiles: List[Tile] = []
        pos_x, pos_y = pos

        for nx, ny in GRID_NEIGHBOURS_9:
            new_x, new_y = pos_x + nx, pos_y + ny
            tile_loc = (new_x, new_y)
            if tile_loc in self.grid_tiles:
                tiles.append(self.grid_tiles[tile_loc])

        return tiles

    def load_map(self, map_id: int):
        map_path = MAP_PATH / f"{map_id}.tmx"
        try:
            map_data = load_pygame(str(map_path))
            self.tilewidth = map_data.tilewidth
            self.tileheight = map_data.tileheight
            self.__cache_tilesets(map_data)

            for layer in map_data.layers:
                if isinstance(layer, TiledTileLayer):
                    self.__load_tile_layer(layer, map_data)
                elif isinstance(layer, TiledObjectGroup):
                    self.__load_object_layer(layer, map_data)

        except Exception as e:
            print(e)

    def __cache_tilesets(self, map_data: "TiledMap"):
        tilesets = [
            tileset
            for tileset in cast(List[TiledTileset], map_data.tilesets)
            if tileset.name not in AVOIDABLE_TILESETS
        ]

        for tileset in tilesets:
            if not tileset.source or not tileset.name:
                continue
            relative_path = tileset.source.split("assets/")[1]
            source = Path(ASSETS_PATH / relative_path)
            self.tileset_cache[tileset.firstgid] = load_image(source)

    def __load_tile_layer(self, layer: "TiledTileLayer", map_data: "TiledMap"):
        for x, y, _ in layer.tiles():
            gid = layer.data[y][x]
            tileset_id = map_data.get_tileset_from_gid(gid).firstgid
            tile = Tile(tileset_id, (x * self.tilewidth, y * self.tileheight))
            props = map_data.get_tile_properties_by_gid(gid)
            if props is not None and props.get("no_collision"):
                self.offgrid.append(Tile(tileset_id, (x, y)))
            else:
                self.grid_tiles[(x, y)] = tile

    def __load_object_layer(self, layer: "TiledObjectGroup", map_data: "TiledMap"):
        for data in layer:
            pass  # later

    def render(self):
        surface = self.game.screen
        scroll = self.game.scroll

        start_x = int(-scroll.x // self.tilewidth)
        end_x = int(start_x + (SCREEN_WIDTH // self.tilewidth))
        start_y = int(-scroll.y // self.tileheight)
        end_y = int(start_y + (SCREEN_HEIGHT // self.tileheight))

        for y in range(start_y, end_y + 1):
            for x in range(start_x, end_x + 1):
                location = (x, y)
                if location not in self.grid_tiles:
                    continue
                tile = self.grid_tiles[location]
                tile_surf = self.tileset_cache[tile.tileset_id]
                pos = tile.pos - scroll
                surface.blit(
                    tile_surf,
                    pos,
                    (
                        x * self.tilewidth,
                        y * self.tileheight,
                        self.tilewidth,
                        self.tileheight,
                    ),
                )
