from typing import TYPE_CHECKING, Callable, Iterable, Literal, Sequence, Union

from entities.base_entity import BaseEntity
from entities.projectile.fire import FireProjectile
from utils.enemy_utils import melee_range

if TYPE_CHECKING:
    from entities.enemy_entity import Bat, FireWorm, Mushroom
    from entities.player import Player

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


def player_hits_enemy(player, enemy):
    if not player.is_attacking:
        return

    if not enemy.hit_timer.has_reached_interval():
        return

    enemy.transition_to("hit")
    player.apply_damage_to_target(enemy)


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


def base_collision(player: "Player", entity: EnemyType, collide_checker: Callable[[BaseEntity, BaseEntity], bool]):
    if not (player.get_state() == "attack" or entity.get_state() == "attack"):
        return

    if collide_checker(player, entity):
        player_hits_enemy(player, entity)
        enemy_hits_player(player, entity)


def melee_enemy_collision(player: "Player", enemy: EnemyType):
    return base_collision(player, enemy, melee_range)


def projectile_collision(entity: "Player", projectiles: Iterable["FireProjectile"]):
    if not entity.hit_timer.has_reached_interval():
        return
    for projectile in projectiles:
        if projectile.rect().colliderect(entity.hitbox()):
            projectile.mark_ready_to_kill()
            entity.transition_to("hit")
            entity.take_damage(0.1)
            break
