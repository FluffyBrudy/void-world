from typing import Dict

import pygame

from constants import ASSETS_PATH, PLAYER_SCALE
from ttypes.index_type import ImageLoadOptions
from utils.animation import Animation, PostAnimatableAnimation
from utils.image_utils import load_image, load_images, load_spritesheet


class AssetManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if not hasattr(self, "assets"):
            self.assets: Dict[str, Animation] = {}
        if not hasattr(self, "icons"):
            self.icons: Dict[str, Dict[str, pygame.Surface]] = {}
        if not hasattr(self, "fonts"):
            self.fonts: Dict[str, pygame.Font] = {}

    def load_all(self) -> None:
        self._load_projectile_assets()
        self._load_player_assets()
        self._load_enemy_assets()
        self._load_icons()
        self._load_fonts()

    def _load_player_assets(self) -> None:
        player_path = ASSETS_PATH / "characters" / "player"

        self.assets.update(
            {
                "player/idle": Animation(
                    load_images(
                        player_path / "idle",
                        scale_ratio_or_size=PLAYER_SCALE,
                        trim_transparent_pixel=(True, (41, 43, 34, 38)),
                    ),
                    0.2,
                ),
                "player/idleturn": Animation(
                    load_spritesheet(
                        player_path / "idle_turn" / "idle_turn.png",
                        (128, 128),
                        scale_ratio_or_size=PLAYER_SCALE,
                        trim_transparent_pixel=(True, None),
                        flip=(True, False),
                    ),
                    animation_speed=0.2,
                    loop=False,
                ),
                "player/run": Animation(
                    load_images(
                        player_path / "run",
                        scale_ratio_or_size=PLAYER_SCALE,
                        trim_transparent_pixel=(True, (44, 43, 43, 40)),
                    ),
                    0.2,
                ),
                "player/jump": Animation(
                    load_images(
                        player_path / "jump",
                        scale_ratio_or_size=PLAYER_SCALE,
                        trim_transparent_pixel=(True, (44, 36, 41, 55)),
                    ),
                    0.2,
                    False,
                ),
                "player/fall": PostAnimatableAnimation(
                    load_spritesheet(
                        player_path / "fall" / "fall_loop.png",
                        (128, 128),
                        scale_ratio_or_size=PLAYER_SCALE,
                        trim_transparent_pixel=(True, (44, 36, 41, 55)),
                    ),
                    load_spritesheet(
                        player_path / "fall" / "fall.png",
                        (128, 128),
                        scale_ratio_or_size=PLAYER_SCALE,
                        trim_transparent_pixel=(True, (44, 36, 41, 55)),
                    ),
                    0.2,
                    0.1,
                    True,
                ),
                "player/attack": Animation(
                    load_images(
                        player_path / "attack",
                        scale_ratio_or_size=PLAYER_SCALE,
                        trim_transparent_pixel=(True, ((52, 42, 63, 47))),
                    ),
                    0.2,
                    False,
                ),
                "player/hit": Animation(
                    load_spritesheet(
                        player_path / "hurt" / "hurt.png",
                        (128, 128),
                        scale_ratio_or_size=PLAYER_SCALE,
                        trim_transparent_pixel=(True, None),
                        flip=(True, False),
                    ),
                    animation_speed=0.2,
                    loop=False,
                ),
                "player/wallslide": Animation(
                    load_spritesheet(
                        player_path / "wallslide" / "wallslide.png",
                        (128, 128),
                        scale_ratio_or_size=PLAYER_SCALE,
                        trim_transparent_pixel=(True, None),
                    ),
                    0.2,
                    False,
                ),
                "player/skillcast": Animation(
                    load_images(
                        player_path / "idle",
                        scale_ratio_or_size=PLAYER_SCALE,
                        trim_transparent_pixel=(True, (41, 43, 34, 38)),
                    ),
                    0.5,
                    False,
                ),
            }
        )

    def _load_enemy_assets(self) -> None:
        self.assets.update(
            {
                "bat/fly": Animation(
                    load_images(
                        ASSETS_PATH / "enemies" / "bat" / "fly",
                        scale_ratio_or_size=PLAYER_SCALE,
                        trim_transparent_pixel=(True, None),
                    ),
                    0.2,
                    True,
                ),
                "bat/chase": Animation(
                    load_images(
                        ASSETS_PATH / "enemies" / "bat" / "fly",
                        scale_ratio_or_size=PLAYER_SCALE,
                        trim_transparent_pixel=(True, None),
                    ),
                    0.2,
                    True,
                ),
                "bat/attack": Animation(
                    load_images(
                        ASSETS_PATH / "enemies" / "bat" / "attack",
                        scale_ratio_or_size=PLAYER_SCALE,
                        trim_transparent_pixel=(True, None),
                    ),
                    0.2,
                    False,
                ),
                "bat/hit": Animation(
                    load_images(
                        ASSETS_PATH / "enemies" / "bat" / "hit",
                        scale_ratio_or_size=PLAYER_SCALE,
                        trim_transparent_pixel=(True, None),
                    ),
                    0.2,
                    True,
                ),
                "mushroom/idle": Animation(
                    load_spritesheet(
                        ASSETS_PATH / "enemies" / "mushroom" / "idle.png",
                        (150, 150),
                        scale_ratio_or_size=PLAYER_SCALE,
                        trim_transparent_pixel=(True, None),
                    )
                ),
                "mushroom/run": Animation(
                    load_spritesheet(
                        ASSETS_PATH / "enemies" / "mushroom" / "run.png",
                        (150, 150),
                        scale_ratio_or_size=PLAYER_SCALE,
                        trim_transparent_pixel=(True, None),
                    )
                ),
                "mushroom/hit": Animation(
                    load_spritesheet(
                        ASSETS_PATH / "enemies" / "mushroom" / "hit.png",
                        (150, 150),
                        scale_ratio_or_size=PLAYER_SCALE,
                        trim_transparent_pixel=(True, None),
                    ),
                    0.2,
                    False,
                ),
                "mushroom/death": Animation(
                    load_spritesheet(
                        ASSETS_PATH / "enemies" / "mushroom" / "death.png",
                        (150, 150),
                        scale_ratio_or_size=PLAYER_SCALE,
                        trim_transparent_pixel=(True, None),
                    ),
                    0.05,
                    False,
                ),
                "mushroom/attack": Animation(
                    load_spritesheet(
                        ASSETS_PATH / "enemies" / "mushroom" / "attack.png",
                        (150, 150),
                        scale_ratio_or_size=PLAYER_SCALE,
                        trim_transparent_pixel=(True, None),
                    ),
                    animation_speed=0.2,
                    loop=False,
                ),
                "fireworm/idle": Animation(
                    load_spritesheet(
                        ASSETS_PATH / "enemies" / "fireworm" / "idle.png",
                        (90, 90),
                        scale_ratio_or_size=PLAYER_SCALE,
                        trim_transparent_pixel=(True, None),
                    ),
                    0.2,
                    True,
                ),
                "fireworm/death": Animation(
                    load_spritesheet(
                        ASSETS_PATH / "enemies" / "fireworm" / "death.png",
                        (90, 90),
                        scale_ratio_or_size=PLAYER_SCALE,
                        trim_transparent_pixel=(True, None),
                    ),
                    0.08,
                    False,
                ),
                "fireworm/hit": Animation(
                    load_spritesheet(
                        ASSETS_PATH / "enemies" / "fireworm" / "hit.png",
                        (90, 90),
                        scale_ratio_or_size=PLAYER_SCALE,
                        trim_transparent_pixel=(True, None),
                    ),
                    0.2,
                    False,
                ),
                "fireworm/run": Animation(
                    load_spritesheet(
                        ASSETS_PATH / "enemies" / "fireworm" / "run.png",
                        (90, 90),
                        scale_ratio_or_size=PLAYER_SCALE,
                        trim_transparent_pixel=(True, None),
                    ),
                    0.2,
                    True,
                ),
                "fireworm/attack": Animation(
                    load_spritesheet(
                        ASSETS_PATH / "enemies" / "fireworm" / "attack.png",
                        (90, 90),
                        scale_ratio_or_size=PLAYER_SCALE,
                        trim_transparent_pixel=(True, None),
                    ),
                    0.2,
                    False,
                ),
            }
        )

    def _load_projectile_assets(self):
        options: ImageLoadOptions = {"trim_transparent_pixel": (True, None)}
        explosion_scale = 2.0
        self.assets.update(
            {
                "projectile/fire": Animation(
                    load_spritesheet(ASSETS_PATH / "projectiles" / "fireball" / "move.png", (46, 46), **options),
                    animation_speed=0.2,
                    loop=True,
                ),
                "projectile/fire_explosion": Animation(
                    load_spritesheet(
                        ASSETS_PATH / "projectiles" / "fireball" / "explosion.png",
                        (46, 46),
                        **{**options, "scale_ratio_or_size": explosion_scale},
                    ),
                    animation_speed=0.2,
                    loop=False,
                ),
            }
        )

    def _load_icons(self) -> None:
        skills_default_options: ImageLoadOptions = {"trim_transparent_pixel": (True, None)}
        self.icons = {
            "player/skills": {
                "dash": load_image(ASSETS_PATH / "icons" / "player" / "skill" / "dash.png", **skills_default_options),
                "heal": load_image(ASSETS_PATH / "icons" / "player" / "skill" / "heal.png", **skills_default_options),
            }
        }

    def _load_fonts(self) -> None:
        self.fonts = {"monogram": pygame.Font(ASSETS_PATH / "fonts" / "monogram.ttf", size=30)}


assets_manager = AssetManager()
