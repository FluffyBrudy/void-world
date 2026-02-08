from typing import TYPE_CHECKING, Callable, Literal, Union

from entities.base_entity import BaseEntity
from entities.player import Player
from entities.projectile.fire import FireProjectile
from utils.combat_utils import direction, melee_range

if TYPE_CHECKING:
    from entities.enemy_entity import Bat, FireWorm, Mushroom

EnemyType = Union["Mushroom", "Bat", "FireWorm"]


def _attack_phase(entity: EnemyType) -> Literal["startup", "active", "finish"]:
    state = entity.current_state
    frame_index = entity.animation.frame_index

    if state.startup_frame == 0:
        return "active"

    if frame_index < state.startup_frame:
        return "startup"
    if frame_index < state.startup_frame + state.active_frame:
        return "active"
    return "finish"


def player_hits_enemy(player: "Player", enemy: EnemyType):
    if not player.is_attacking:
        return

    if not enemy.hit_timer.has_reached_interval():
        return

    enemy.transition_to("hit")
    player.apply_damage_to_target(enemy)
    enemy.knockback(direction(player, enemy, scale=2.0))


def enemy_hits_player(player, enemy):
    if enemy.get_state() != "attack":
        return

    if not player.hit_timer.has_reached_interval():
        return

    if player.is_dashing:
        return

    if _attack_phase(enemy) != "active":
        return

    player.transition_to("hit")
    player.take_damage(enemy.stats["damage"])
    player.knockback(direction(enemy, player))


def base_collision(player: "Player", entity: EnemyType, collide_checker: Callable[[BaseEntity, BaseEntity], bool]):
    if not (player.get_state() == "attack" or entity.get_state() == "attack"):
        return

    if collide_checker(player, entity):
        player_hits_enemy(player, entity)
        enemy_hits_player(player, entity)


def melee_enemy_collision(player: "Player", enemy: EnemyType):
    return base_collision(player, enemy, melee_range)


def projectile_collision(projectile: "FireProjectile", entity: "Player"):
    if not entity.hit_timer.has_reached_interval():
        return False

    if projectile.rect().colliderect(entity.hitbox()):
        if isinstance(entity, Player) and entity.is_immune():
            return False
        else:
            projectile.mark_ready_to_kill()
            entity.transition_to("hit")
            entity.take_damage(0.1)
            entity.knockback(direction(projectile, entity))
            return True

    return False
