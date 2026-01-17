from typing import TYPE_CHECKING
from pydebug import pgdebug

if TYPE_CHECKING:
    from entities.player import Player
    from entities.enemy_entity import Bat, Mushroom


def player_bat_collision(player: "Player", bat: "Bat", /):
    state = bat.get_state()

    if state == "hit" or not player.hit_timer.has_reach_interval():
        return

    if state not in {"chase", "attack"}:
        return

    if player.attack_hitbox().colliderect(bat.hitbox()):
        if state == "chase" and player.is_attacking:
            bat.transition_to("hit")
        elif state == "attack" and not player.is_dashing:
            player.transition_to("hit")


def player_mushroom_collision(player: "Player", mushroom: "Mushroom", /):
    state = mushroom.get_state()

    if state == "hit" or not player.hit_timer.has_reach_interval():
        return

    if state not in {"run", "attack"}:
        return
    if player.attack_hitbox().colliderect(mushroom.hitbox()):
        if state == "run" and player.is_attacking:
            mushroom.transition_to("hit")
        elif state == "attack" and not player.is_dashing:
            player.transition_to("hit")
