from pathlib import Path

SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
FPS = 60

BASE_PATH = Path.cwd().parent
ASSETS_PATH = BASE_PATH / "assets"
MAP_PATH = BASE_PATH / "tilemap" / "tmx"

BASE_SPEED = 150
GRAVITY = 1200
WALL_FRICTION_COEFFICIENT = 0.1
MAX_FALL_SPEED = 1800
JUMP_DISTANCE = int(MAX_FALL_SPEED // 4)
# fmt: off
GRID_NEIGHBOURS_9 = (
	(-1, -1), (0, -1), (1, -1),
	(-1, 0),  (0, 0),  (1, 0),
	(-1, 1),  (0, 1),  (1, 1)
)
# fmt: on
