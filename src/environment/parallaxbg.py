from pathlib import Path
from typing import TYPE_CHECKING
from utils.image_utils import load_image

if TYPE_CHECKING:
    from game import Game


class ParallaxBg:
    game: "Game" = None  # type:  ignore

    def __init__(self, path: Path) -> None:
        self.parallax_bgs = [
            load_image(path, scale_ratio_or_size=(self.game.screen.size))
            for path in path.iterdir()
        ]

    def update(self):
        pass

    def render(self):
        self.game.screen.blit(self.parallax_bgs[0], (0, 0))
