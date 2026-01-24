from math import pi
from random import uniform
from typing import Dict, Tuple, override

import pygame

from constants import (
    BASE_SPEED,
    GRAVITY,
    JUMP_DISTANCE,
    MAX_FALL_SPEED,
    WALL_FRICTION_COEFFICIENT,
)
from effects.particles import coned_particles
from entities.physics_entity import PhysicsEntity
from entities.states.player_fsm import (
    AttackState,
    FallState,
    HitState,
    IdleState,
    IdleTurnState,
    JumpState,
    RunState,
    SlideState,
)
from ttypes.index_type import TPosType
from ui.widgets.progressbar import ProgressBarUI
from utils.timer import Timer

TAttackSizes = Dict[str, Tuple[int, int]]

PARTICLE_DIR_LEFT = (-pi / 12, pi / 12)
PARTICLE_DIR_RIGHT = (pi - (pi / 12), pi - (-pi / 12))


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
            "hit": HitState(),
        }
        super().__init__("player", pos, size, states, offset)
        self.movement_start_timer = Timer(200)

        self.is_attacking = False
        self.attack_timer = Timer(300, True)

        self.is_dashing = False
        self.dash_timer = Timer(2000, True)
        self.hit_timer = Timer(2000, True)

        self.healthbar = ProgressBarUI(fill_color="lime")  # type: ignore
        self.manabar = ProgressBarUI(fill_color="skyblue", margin_y=int(self.healthbar.fullsize[1] * 1.4))  # type: ignore

        self.stats: Dict[str, float] = {"health": 1.0, "damage": 0.1}

    def take_damage(self, damage: float):
        self.stats["health"] -= damage
        self.healthbar.set_progress(self.stats["health"])

    def set_attack_size(self, offsets: TAttackSizes):
        self.attack_sizes = offsets

    def attack_hitbox(self):
        """this version is valid, just need scale"""
        hbox = self.hitbox()
        if self.current_state.name != "attack":
            return hbox
        attack_w, attack_h = self.attack_sizes[self.current_state.name]
        offset_x = (hbox.centerx - attack_w) if self.flipped else hbox.centerx
        return pygame.Rect(offset_x, hbox.top, attack_w, attack_h)

    def input(self):
        if self.is_dashing or self.get_state() == "hit":
            return

        keys = pygame.key.get_pressed()

        input_vector = pygame.Vector2(0, 0)

        if keys[pygame.K_SPACE]:
            self.dash()

        if keys[pygame.K_LEFT]:
            if not self.flipped:
                self.flipped = True
                self.transition_to("idleturn")
            if self.movement_start_timer.has_reached_interval():
                input_vector.x -= 2
        elif keys[pygame.K_RIGHT]:
            if self.flipped:
                self.flipped = False
                self.transition_to("idleturn")
            if self.movement_start_timer.has_reached_interval():
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
            and ((self.contact_sides["left"] and self.flipped) or (self.contact_sides["right"] and not self.flipped))
            and not self.contact_sides["down"]
            and self.game.tilemap.is_solid_tile((pos_x, hitbox.bottom))
        )

    def jump(self):
        self.velocity.y = int(-JUMP_DISTANCE * 2)

    def attack(self):
        if self.get_state() == "hit":
            return
        if not self.is_attacking and self.attack_timer.has_reached_interval():
            self.transition_to("attack")
            self.is_attacking = True

    def dash(self):
        if (
            not self.current_state.name == "wallslide"
            and not self.is_dashing
            and self.dash_timer.has_reached_interval()
        ):
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

        if self.dash_timer.has_reached(0.15) or (
            (self.contact_sides["left"] and self.flipped) or (self.contact_sides["right"] and not self.flipped)
        ):
            self.is_dashing = False
            self.velocity.x = 0  # because if x-comonent of velocity is not resett it keeps dashing
        pm = self.game.particle_manager
        pos = self.hitbox().center
        coned_particles(
            pos,
            tuple(uniform(*PARTICLE_DIR_LEFT) for _ in range(5))
            if self.flipped
            else tuple(uniform(*PARTICLE_DIR_RIGHT) for _ in range(5)),
            pm,
            color=(0, 255, 255),
            filled=True,
        )

    @override
    def update(self, dt: float):
        self.input()
        if self.is_attacking:
            self.velocity.x = 0
        if self.can_slide():
            self.velocity.y = min(self.velocity.y, MAX_FALL_SPEED * WALL_FRICTION_COEFFICIENT)
        self.healthbar.update()
        self.manabar.update()
        super().update(dt)

    @override
    def manage_state(self):
        if self.is_attacking and self.animation.has_animation_end():
            self.is_attacking = False
            self.attack_timer.reset_to_now()
        self.manage_dash()
        super().manage_state()

    def render(self, surface: pygame.Surface, offset: TPosType):
        if not self.is_dashing:
            frame, pos = self.get_renderable(offset)
            frame_copy = frame.copy()
            surface.blit(frame_copy, pos)

        self.healthbar.render(surface)
        self.manabar.render(surface)
