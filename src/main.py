import pygame
from constants import ASSETS_PATH, FPS, SCREEN_HEIGHT, SCREEN_WIDTH
from entities.physics_entity import PhysicsEntity, Player
from lib.tilemap import Tilemap
from pydebug import Debug
from utils.image_utils import load_images
from utils.animation import Animation


class Game:
    def __init__(self) -> None:
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()

        self.scroll = pygame.Vector2(0, 0)
        self.running = True
        interface_classes = (PhysicsEntity, Tilemap)
        for interface in interface_classes:
            interface.game = self

        player_path = ASSETS_PATH / "characters" / "blue-sprite"
        self.assets = {
            "player/idle": Animation(load_images(player_path / "idle"), 0.1),
            "player/run": Animation(load_images(player_path / "run"), 0.15),
            "player/jump": Animation(load_images(player_path / "jump"), 0.2, False),
            "player/attack": Animation(load_images(player_path / "attack"), 0.2, False),
            # "player/shoot": Animation(load_images(player_path / "Shoot")),
        }
        self.level = 0

        self.player = Player((100, -400), (25, 35), (5, 3))

        self.tilemap = Tilemap(tile_scale=2.5)
        init_load = self.tilemap.load_map(0)
        if not init_load:
            raise Exception("tilemap not initialized")

    def handle_event(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    def handle_camera(self):
        sw, sh = self.screen.size
        player_rect = self.player.rect()
        target_scroll_x = player_rect.centerx - sw // 2
        target_scroll_y = player_rect.centery - sh // 2
        scroll_x, scroll_y = self.scroll

        self.scroll.x = scroll_x + (target_scroll_x - scroll_x) * 0.1
        self.scroll.y = scroll_y + (target_scroll_y - scroll_y) * 0.05

    def update(self):
        dt = self.clock.tick(FPS) / 1000.0
        self.handle_event()
        self.handle_camera()
        self.player.update(dt)

    def render_all(self):
        self.screen.fill((50, 50, 100))
        self.player.render()
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
