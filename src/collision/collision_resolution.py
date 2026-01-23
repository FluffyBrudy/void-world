from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from entities.enemy_entity import Bat, Mushroom
    from entities.player import Player


def player_bat_collision(player: "Player", bat: "Bat", /):
    state = bat.get_state()

    if state == "hit" or not player.hit_timer.has_reached_interval():
        return

    if state not in {"chase", "attack"}:
        return

    if player.attack_hitbox().colliderect(bat.hitbox()):
        if state == "chase" and player.is_attacking:
            bat.transition_to("hit")
            bat.take_damage(0.1)
        elif state == "attack" and not player.is_dashing and bat.animation.frame_index >= bat.animation.frames_len // 2:
            player.transition_to("hit")
            player.take_damage(0.1)


def player_mushroom_collision(player: "Player", mushroom: "Mushroom", /):
    state = mushroom.get_state()

    if state == "hit" or not player.hit_timer.has_reached_interval():
        return

    if state not in {"run", "attack"}:
        return
    if player.attack_hitbox().colliderect(mushroom.hitbox()):
        if state == "run" and player.is_attacking:
            mushroom.transition_to("hit")
        elif (
            state == "attack"
            and not player.is_dashing
            and mushroom.animation.frame_index >= mushroom.animation.frames_len // 2
        ):
            player.transition_to("hit")
            player.take_damage(0.1)
