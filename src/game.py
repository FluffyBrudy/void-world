from itertools import chain

import pygame

from collision.collision_resolution import base_collision, melee_enemy_collision, projectile_collision
from constants import (
    ASSETS_PATH,
    DEADZONE_CAMERA_THRESHOLD_X,
    FPS,
    PLAYER_SCALE,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    TILEMAP_SCALE,
)
from entities.base_entity import BaseEntity
from entities.enemy_entity import Bat, Enemy, FireWorm, Mushroom
from entities.player import Player
from entities.projectile.fire import FireProjectile
from environment.parallaxbg import ParallaxBg
from lib.tilemap import Tilemap
from managers.asset_manager import assets_manager
from particle.particle_manager import ParticleManager
from pydebug import Debug
from ui.widgets.overlay import CooldownOverlay
from ui.widgets.playerhud import PlayerHUD


class Game:
    def __init__(self) -> None:
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()

        self.scroll = pygame.Vector2(0, 0)
        self.running = True
        interface_classes = (
            BaseEntity,
            Tilemap,
            ParallaxBg,
            ParticleManager,
            Enemy,
            CooldownOverlay,
            PlayerHUD,
        )
        for interface in interface_classes:
            interface.game = self

        assets_manager.load_all()

        self.level = 0

        player_base_size = assets_manager.assets["player/idle"].get_frame().size
        self.player = Player((2000, 200), player_base_size, (0, 0))
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

        self.particle_manager = ParticleManager()

        bat = Bat((800, 0), assets_manager.assets["bat/fly"].get_frame().size)
        mushroom = Mushroom((800, 0), assets_manager.assets["bat/fly"].get_frame().size, (0, -20))
        fireworm = FireWorm((1200, 0), assets_manager.assets["fireworm/idle"].get_frame().size, (0, -20))

        bat.set_target(self.player)
        mushroom.set_target(self.player)
        fireworm.set_target(self.player)

        self.player_hud = PlayerHUD(self.player)

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

    def handle_collision(self):
        player = self.player
        collision_enemies = chain(Bat.get_by_group(), Mushroom.get_by_group())
        for enemy in collision_enemies:
            melee_enemy_collision(player, enemy)

        collision_projectiles = chain(FireProjectile.get_instances())
        projectile_collision(player, collision_projectiles)

    def update(self):
        dt = self.clock.tick(FPS) / 1000.0
        self.dt = dt
        self.handle_event()
        self.deadzone_camera()
        self.handle_collision()
        self.player.update(dt)

    def render_all(self):
        self.screen.fill((50, 50, 100))
        self.parallaxbg.render()

        BaseEntity.render_all(self.screen, self.dt, self.scroll)
        self.player.render(self.screen, self.scroll)
        FireProjectile.render_all(self.screen, self.dt, self.scroll)
        self.tilemap.render()

        Debug.draw_all(self.screen)

        self.particle_manager.render(self.screen, self.dt)

        self.player_hud.update()
        self.player_hud.render(self.screen)

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
