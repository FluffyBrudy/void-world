from typing import Tuple, override
import pygame
from constants import (
    BASE_SPEED,
    GRAVITY,
    JUMP_DISTANCE,
    MAX_FALL_SPEED,
    WALL_FRICTION_COEFFICIENT,
)
from entities.states.player_fsm import (
    AttackState,
    FallState,
    IdleState,
    IdleTurnState,
    JumpState,
    RunState,
    SlideState,
)
from entities.physics_entity import PhysicsEntity
from pydebug import pgdebug
from utils.timer import Timer


class Player(PhysicsEntity):
    def __init__(
        self,
        pos: Tuple[int, int],
        size: Tuple[int, int],
        offset: Tuple[int, int] = (0, 0),
    ):
        states = {
            "idle": IdleState(),
            "run": RunState(),
            "jump": JumpState(),
            "attack": AttackState(),
            "idleturn": IdleTurnState(),
            "fall": FallState(),
            "wallslide": SlideState(),
        }
        super().__init__("player", pos, size, states, offset)
        self.movement_start_timer = Timer(200)

        self.is_attacking = False
        self.attack_timer = Timer(300)

        self.is_dashing = False
        self.dash_timer = Timer(2000)

    def attack_hitbox(self):
        x, y, w, h = self.hitbox()
        multiplier = -1 if self.flipped else 1
        return pygame.Rect(x + multiplier * w * 0.3, y, w, h)

    def input(self):
        if self.is_dashing:
            return

        keys = pygame.key.get_pressed()

        input_vector = pygame.Vector2(0, 0)

        if keys[pygame.K_SPACE]:
            self.dash()

        if keys[pygame.K_LEFT]:
            if not self.flipped:
                self.flipped = True
                self.set_state("idleturn")
            if self.movement_start_timer.has_reach_interval():
                input_vector.x -= 2
        elif keys[pygame.K_RIGHT]:
            if self.flipped:
                self.flipped = False
                self.set_state("idleturn")
            if self.movement_start_timer.has_reach_interval():
                input_vector.x += 2
        else:
            self.movement_start_timer.reset_to_now()

        if self.current_state.name in ("idle", "run", "jump"):
            if keys[pygame.K_UP]:
                self.jump()
        if keys[pygame.K_f] or keys[pygame.K_RETURN]:
            self.attack()

        if input_vector:
            self.velocity.x = input_vector.x
        else:
            self.velocity.x = 0

    def can_slide(self):
        hitbox = self.hitbox()
        pos_x = hitbox.right
        if self.flipped:
            pos_x = hitbox.left - self.game.tilemap.tilewidth
        return (
            self.velocity.y > 0
            and (
                (self.contact_sides["left"] and self.flipped)
                or (self.contact_sides["right"] and not self.flipped)
            )
            and not self.contact_sides["down"]
            and self.game.tilemap.is_solid_tile((pos_x, hitbox.bottom))
        )

    def jump(self):
        self.velocity.y = int(-JUMP_DISTANCE * 2)

    def attack(self):
        if not self.is_attacking and self.attack_timer.has_reach_interval():
            self.set_state("attack")
            self.is_attacking = True

    def dash(self):
        if not self.is_dashing and self.dash_timer.has_reach_interval():
            self.is_dashing = True
            self.dash_timer.reset_to_now()

    def handle_movement(self, dt: float):
        frame_movement_x = (self.velocity.x) * (BASE_SPEED * dt)
        self.pos[0] += frame_movement_x
        self.collision_horizontal()

        self.velocity.y += GRAVITY * dt
        self.pos[1] += self.velocity.y * dt
        self.collision_vertical()

    def manage_dash(self):
        if not self.is_dashing:
            return

        direction = -1 if self.flipped else 1
        self.velocity.x = 15 * direction  # velocity requires direction
        self.velocity.y = 0  # otherwise it will have trajectory path

        if self.dash_timer.has_reached(0.15):
            self.is_dashing = False
            self.velocity.x = (
                0  # because if x-comonent of velocity is not resett it keeps dashing
            )

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
        self.manage_dash()
        super().manage_state()

    def render(self, surface: pygame.Surface):
        # hbox = self.attack_hitbox()
        # pos = hbox.topleft - self.game.scroll
        # pgdebug_rect(self.game.screen, (pos, hbox.size))
        return super().render(surface)
