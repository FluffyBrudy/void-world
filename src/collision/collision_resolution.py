from typing import TYPE_CHECKING, Literal, Union

from entities.projectile.fire import FireProjectile

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


def base_collision(player: "Player", entity: EnemyType):
    if not (player.get_state() == "attack" or entity.get_state() == "attack"):
        return

    state = entity.get_state()

    if player.attack_hitbox().colliderect(entity.hitbox()):
        if player.is_attacking and entity.hit_timer.has_reached_interval():
            entity.transition_to("hit")
            player.apply_damage_to_target(entity)
        elif (
            state == "attack"
            and player.hit_timer.has_reached_interval()
            and not player.is_dashing
            and _attack_phase(entity) == "active"
        ):
            player.transition_to("hit")
            player.take_damage(entity.stats["damage"])
