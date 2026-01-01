from typing import (
    TYPE_CHECKING,
    Dict,
    Literal,
    Tuple,
    override,
)
import pygame
from constants import (
    BASE_SPEED,
    GRAVITY,
    JUMP_DISTANCE,
    MAX_FALL_SPEED,
    WALL_FRICTION_COEFFICIENT,
)
from lib.state import (
    AttackState,
    FallState,
    IdleState,
    IdleTurnState,
    JumpState,
    RunState,
    SlideState,
    State,
)
from pydebug import pgdebug, pgdebug_rect
from utils.timer import Timer

if TYPE_CHECKING:
    from game import Game


T4Directions = Literal["up", "down", "left", "right"]
TContactSides = Dict[T4Directions, bool]


class PhysicsEntity:
    game: "Game" = None  # type: ignore

    def __init__(
        self,
        etype: str,
        pos: Tuple[int, int],
        size: Tuple[int, int],
        offset: Tuple[int, int] = (0, 0),
    ):
        super().__init__()

        self.states: Dict[str, State] = {
            "idle": IdleState(),
            "run": RunState(),
            "jump": JumpState(),
            "attack": AttackState(),
        }
        self.current_state: State = self.states["idle"]

        self.animation = self.game.assets[etype + "/" + "idle"]

        self.etype = etype

        self.velocity = pygame.Vector2()

        self.flipped = False

        self.contact_sides: TContactSides = {
            "left": False,
            "right": False,
            "up": False,
            "down": False,
        }

        self.animation = self.game.assets[etype + "/" + self.current_state.name]

        self.offset = offset
        self.pos = pygame.Vector2(pos)
        self.size = size

    def rect(self):
        return pygame.Rect(self.pos, self.size)

    def hitbox(self):
        x, y = self.pos
        ox, oy = self.offset
        new_w, new_h = self.size[0] - 2 * ox, self.size[1] - 2 * oy
        new_y = oy + y
        new_x = x + ox
        return pygame.Rect(new_x, new_y, new_w, new_h)

    def grounded(self):
        return self.contact_sides["down"]

    def set_state(self, new_state: str):
        if new_state != self.current_state.name:
            self.current_state = self.states[new_state]
            self.animation = self.game.assets[self.etype + "/" + new_state].copy()

    def manage_state(self):
        next_state = self.current_state.can_transition(self)
        if next_state is not None:
            self.current_state.exit(self)
            self.set_state(next_state)
            self.current_state.enter(self)

    def collision_horizontal(self):
        tiles = self.game.tilemap.physics_rect_around(self.pos)
        hitbox = self.hitbox()

        for tile in tiles:
            if tile.colliderect(hitbox):
                if self.velocity.x < 0:
                    self.pos.x += tile.right - hitbox.left
                elif self.velocity.x > 0:
                    self.pos.x -= hitbox.right - tile.left
                self.velocity.x = 0
                break

    def collision_vertical(self):
        tiles_rect_around = self.game.tilemap.physics_rect_around(self.pos)
        hitbox = self.hitbox()
        delta = 0

        for tile_rect in tiles_rect_around:
            if tile_rect.colliderect(hitbox):
                if self.velocity.y < 0:
                    delta = tile_rect.bottom - hitbox.top
                    self.velocity.y = 0
                elif self.velocity.y > 0:
                    delta = tile_rect.top - hitbox.bottom
                    self.velocity.y = 0
                self.pos[1] += delta
                break

    def identify_contact_sides(self):
        tiles_rect_around = self.game.tilemap.physics_rect_around(self.pos)

        hitbox = self.hitbox()
        self.contact_sides["left"] = (
            hitbox.move(-1, 0).collidelist(tiles_rect_around) >= 0
        )
        self.contact_sides["right"] = (
            hitbox.move(1, 0).collidelist(tiles_rect_around) >= 0
        )
        self.contact_sides["down"] = (
            hitbox.move(0, 1).collidelist(tiles_rect_around) >= 0
        )
        self.contact_sides["up"] = (
            hitbox.move(0, -1).collidelist(tiles_rect_around) >= 0
        )

    def handle_movement(self, dt: float):
        frame_movement_x = (self.velocity.x) * (BASE_SPEED * dt)
        self.pos[0] += frame_movement_x
        self.collision_horizontal()

        self.velocity.y += GRAVITY * dt
        self.pos[1] += self.velocity.y * dt
        self.collision_vertical()

    def update(self, dt: float):
        self.handle_movement(dt)
        self.identify_contact_sides()
        self.manage_state()
        self.animation.update()
        pgdebug("fall" if self.velocity.y > 0 and not self.grounded() else "")

    def render(self):
        frame = self.animation.get_frame()
        render_pos = self.pos - self.game.scroll

        if self.flipped:
            frame = pygame.transform.flip(frame, True, False)

        render_pos.x += (self.size[0] - frame.get_width()) / 2
        render_pos.y += (self.size[1] - frame.get_height()) / 2

        self.game.screen.blit(frame, render_pos)


class Player(PhysicsEntity):
    def __init__(
        self,
        pos: Tuple[int, int],
        size: Tuple[int, int],
        offset: Tuple[int, int] = (0, 0),
    ):
        super().__init__("player", pos, size, offset)
        self.is_attacking = False
        self.flip_timer = Timer(200)
        self.attack_timer = Timer(300)

        self.states = {
            **self.states,
            "idleturn": IdleTurnState(),
            "fall": FallState(),
            "wallslide": SlideState(),
        }

    def attack_hitbox(self):
        x, y, w, h = self.hitbox()
        multiplier = -1 if self.flipped else 1
        return pygame.Rect(x + multiplier * w * 0.3, y, w, h)

    def input(self):
        keys = pygame.key.get_pressed()

        input_vector = pygame.Vector2(0, 0)
        if keys[pygame.K_LEFT]:
            if not self.flipped:
                self.flipped = True
                self.set_state("idleturn")

            if self.flip_timer.has_reach_interval():
                input_vector.x -= 2

        elif keys[pygame.K_RIGHT]:
            if self.flipped:
                self.flipped = False
                self.set_state("idleturn")

            if self.flip_timer.has_reach_interval():
                input_vector.x += 2
        else:
            self.flip_timer.reset_to_now()

        if self.current_state.name in ("idle", "run"):
            if keys[pygame.K_UP]:
                self.jump()
        if keys[pygame.K_SPACE]:
            self.attack()

        if input_vector:
            self.velocity.x = input_vector.x
        else:
            self.velocity.x = 0

    def can_slide(self):
        return (
            self.velocity.y > 0
            and (
                (self.contact_sides["left"] and self.flipped)
                or (self.contact_sides["right"] and not self.flipped)
            )
            and not self.contact_sides["down"]
        )

    def jump(self):
        self.velocity.y = int(-JUMP_DISTANCE * 2)
        self.is_jumping = True

    def attack(self):
        if not self.is_attacking and self.attack_timer.has_reach_interval():
            self.set_state("attack")
            self.is_attacking = True

    @override
    def update(self, dt: float):
        self.input()
        if self.is_attacking:
            self.velocity.x = 0
        if self.can_slide():
            self.velocity.y = min(
                self.velocity.y, MAX_FALL_SPEED * WALL_FRICTION_COEFFICIENT
            )
        super().update(dt)

    @override
    def manage_state(self):
        if self.is_attacking and self.animation.has_animation_end():
            self.is_attacking = False
            self.attack_timer.reset_to_now()
        super().manage_state()

    def render(self):
        # hbox = self.attack_hitbox()
        # pos = hbox.topleft - self.game.scroll
        # pgdebug_rect(self.game.screen, (pos, hbox.size))
        pgdebug(self.is_attacking)
        return super().render()
