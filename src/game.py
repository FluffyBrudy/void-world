from typing import Dict
import pygame
from collision.collision_resolution import (
    player_bat_collision,
    player_mushroom_collision,
)
from constants import (
    ASSETS_PATH,
    DEADZONE_CAMERA_THRESHOLD_X,
    FPS,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
)
from entities.enemy_entity import Bat, Mushroom
from entities.base_entity import BaseEntity
from entities.player import Player
from environment.parallaxbg import ParallaxBg
from lib.tilemap import Tilemap
from pydebug import Debug, pgdebug
from utils.image_utils import load_images, load_spritesheet
from utils.animation import Animation, PostAnimatableAnimation

TILEMAP_SCALE = 5
PLAYER_SCALE = TILEMAP_SCALE / 2.5


class Game:
    def __init__(self) -> None:
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()

        self.scroll = pygame.Vector2(0, 0)
        self.running = True
        interface_classes = (BaseEntity, Tilemap, ParallaxBg)
        for interface in interface_classes:
            interface.game = self

        player_path = ASSETS_PATH / "characters" / "player"

        self.assets: Dict[str, Animation] = {
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
                )
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
        }

        self.level = 0

        player_base_size = self.assets["player/idle"].get_frame().size
        self.player = Player((400, -400), player_base_size, (0, 0))
        self.player.set_attack_size(
            {
                "attack": (int(32 * PLAYER_SCALE), int(43 * PLAYER_SCALE)),
                "attack1": (0, 0),
                "attack2": (0, 0),
            }
        )

        self.tilemap = Tilemap(tile_scale=TILEMAP_SCALE)
        init_load = self.tilemap.load_map(0)
        if not init_load:
            raise Exception("tilemap not initialized")

        self.parallaxbg = ParallaxBg(ASSETS_PATH / "parallax")

        bat = Bat((800, 0), self.assets["bat/fly"].get_frame().size)
        mushroom = Mushroom((1200, 0), self.assets["bat/fly"].get_frame().size)
        bat.set_target(self.player)
        mushroom.set_target(self.player)

    def handle_event(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    def player_center_camera(self):
        sw, sh = self.screen.size
        player_rect = self.player.rect()
        target_scroll_x = player_rect.centerx - sw // 2
        target_scroll_y = player_rect.centery - sh // 2
        scroll_x, scroll_y = self.scroll

        self.scroll.x = scroll_x + (target_scroll_x - scroll_x) * 0.1
        self.scroll.y = scroll_y + (target_scroll_y - scroll_y) * 0.05

    def deadzone_camera(self):
        sh = self.screen.size[1]
        player_rect = self.player.rect()
        scroll_x, scroll_y = self.scroll
        target_scroll_x = scroll_x
        target_scroll_y = player_rect.centery - sh // 2

        if player_rect.centerx < scroll_x + DEADZONE_CAMERA_THRESHOLD_X[0]:
            target_scroll_x = player_rect.centerx - DEADZONE_CAMERA_THRESHOLD_X[0]
        elif player_rect.centerx > scroll_x + DEADZONE_CAMERA_THRESHOLD_X[1]:
            target_scroll_x = player_rect.centerx - DEADZONE_CAMERA_THRESHOLD_X[1]

        self.scroll.x += (target_scroll_x - scroll_x) * 0.1
        self.scroll.y += (target_scroll_y - scroll_y) * 0.05
        pgdebug(self.scroll)

    def handle_collision(self):
        player = self.player
        for bat in Bat.get_by_group():
            player_bat_collision(player, bat)
        for mushroom in Mushroom.get_by_group():
            player_mushroom_collision(player, mushroom)

    def update(self):
        dt = self.clock.tick(FPS) / 1000.0
        self.dt = dt
        self.handle_event()
        self.deadzone_camera()
        self.handle_collision()
        self.player.update(dt)
        pgdebug(f"player={self.player.hit_timer.has_reach_interval()}", 0)

    def render_all(self):
        self.screen.fill((50, 50, 100))
        self.parallaxbg.render()
        self.player.render(self.screen)
        BaseEntity.render_all(self.dt)
        self.tilemap.render()
        Debug.draw_all(self.screen)
        pygame.display.flip()


if __name__ == "__main__":
    # pygame.init()
    # screen = pygame.display.set_mode()
    # tilemap = Tilemap()
    # tilemap.load_map(0)
    game = Game()
    while game.running:
        game.handle_event()
        game.update()
        game.render_all()
    pygame.quit()
