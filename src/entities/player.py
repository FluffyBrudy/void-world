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
from entities.states.fsm import (
    AttackState,
    FallState,
    IdleState,
    IdleTurnState,
    JumpState,
    RunState,
    SlideState,
    State,
)
from entities.physics_entity import PhysicsEntity
from pydebug import pgdebug, pgdebug_rect
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
        self.is_attacking = False
        self.flip_timer = Timer(200)
        self.attack_timer = Timer(300)

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
