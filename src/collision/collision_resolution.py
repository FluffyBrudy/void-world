from typing import TYPE_CHECKING

from pydebug import pgdebug

if TYPE_CHECKING:
    from entities.player import Player
    from entities.enemy_entity import Bat


def player_bat_collision(player: "Player", bat: "Bat"):
    pgdebug(f"has={bat.get_state()}")
    if bat.get_state() == "hit" or not player.hit_timer.has_reach_interval():
        return
    if bat.get_state() == "chase":
        if player.is_attacking and player.attack_hitbox().colliderect(bat.hitbox()):
            bat.transition_to("hit")
    elif bat.get_state() == "attack":
        player.transition_to("hit")
