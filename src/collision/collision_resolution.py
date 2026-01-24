from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from entities.enemy_entity import Bat, Mushroom
    from entities.player import Player


def player_bat_collision(player: "Player", bat: "Bat", /):
    _base_collision(player, bat)


def player_mushroom_collision(player: "Player", mushroom: "Mushroom", /):
    _base_collision(player, mushroom)


def _attack_phase(entity: "Player |  Mushroom | Bat") -> Literal["startup", "active", "finish"]:
    state = entity.current_state
    frame_index = entity.animation.frame_index

    if frame_index < state.startup_frame:
        return "startup"
    if frame_index < state.startup_frame + state.active_frame:
        return "active"
    return "finish"


def _base_collision(player: "Player", entity: "Mushroom | Bat"):
    if not (player.get_state() == "attack" or entity.get_state() == "attack"):
        return

    state = entity.get_state()

    if player.attack_hitbox().colliderect(entity.hitbox()):
        if player.is_attacking and entity.hit_timer.has_reached_interval():
            entity.transition_to("hit")
            entity.take_damage(player.stats["damage"])
        elif (
            state == "attack"
            and player.hit_timer.has_reached_interval()
            and not player.is_dashing
            and _attack_phase(entity) == "active"
        ):
            player.transition_to("hit")
            player.take_damage(entity.stats["damage"])
