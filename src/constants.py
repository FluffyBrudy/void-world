from pathlib import Path

SCREEN_WIDTH = 900
SCREEN_HEIGHT = 700
FPS = 60

BASE_PATH = Path.cwd().parent
ASSETS_PATH = BASE_PATH / "assets"
MAP_PATH = BASE_PATH / "tilemap" / "tmx"

BASE_SPEED = 100
# fmt: off
GRID_NEIGHBOURS_9 = (
	(-1, -1), (0, -1), (1, -1),
	(-1, 0),  (0, 0),  (1, 0),
	(-1, 1),  (0, 1),  (1, 1)
)
# fmt: on
