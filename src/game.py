import pygame
from constants import ASSETS_PATH, SCREEN_HEIGHT, SCREEN_WIDTH
from entities.physics_entity import PhysicsEntity, Player
from lib.tile import AreaTile
from lib.tilemap import Tilemap
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

        player_path = ASSETS_PATH / "characters" / "Blue Sprite"
        self.assets = {
            "player/idle": Animation(load_images(player_path / "Idle"), 0.01),
            "player/run": Animation(load_images(player_path / "Run"), 0.03),
            "player/jump": Animation(load_images(player_path / "Jump")),
            "player/attack": Animation(load_images(player_path / "Attack")),
            # "player/shoot": Animation(load_images(player_path / "Shoot")),
        }
        self.level = 0

        self.player = Player("player", (100, 100), (32, 64))
        print(Tilemap.game)
        self.tilemap = Tilemap()
        self.movement_x = [0, 0]

    def handle_event(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT:
                    self.movement_x[1] = 1
                elif event.key == pygame.K_LEFT:
                    self.movement_x[0] = 1
                elif event.key == pygame.K_UP:
                    self.player.jump()
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_RIGHT:
                    self.movement_x[1] = 0
                elif event.key == pygame.K_LEFT:
                    self.movement_x[0] = 0

    def handle_camera(self):
        sw, sh = self.screen.size
        target_scroll_x = self.player.rect.centerx - sw // 2
        target_scroll_y = self.player.rect.centery - sh // 2
        print(self.scroll, self.player.rect.center)
        scroll_x, scroll_y = self.scroll

        self.scroll.x = scroll_x + (target_scroll_x - scroll_x) * 0.1
        self.scroll.y = scroll_y + (target_scroll_y - scroll_y) * 0.05

    def update(self):
        dt = self.clock.tick() / 1000.0
        self.handle_camera()
        movement_x = self.movement_x
        self.player.update(dt, (movement_x[1] - movement_x[0], 0))

    def render_all(self):
        self.screen.fill((50, 50, 100))
        self.player.render()
        self.tilemap.render()
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
