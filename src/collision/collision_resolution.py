from typing import TYPE_CHECKING

from constants import BASE_SPEED
from entities.enemy_entity import Bat
from pydebug import pgdebug
from utils.math_utils import circle_collision


if TYPE_CHECKING:
    from entities.player import Player


def player_bat_collision(player: "Player", bat: "Bat"):
    collided = circle_collision(
        bat.pos, player.pos, 500, player.size[0], player.size[0] // 2
    )
    if collided[0]:
        vector_dir = (player.pos - bat.pos).normalize()
        bat.velocity = vector_dir * BASE_SPEED
        bat.flipped = True if vector_dir.x < 0 else False
        if collided[1]:
            bat.velocity.x = 0
            bat.velocity.y = 0
            bat.flipped = player.flipped
            bat.set_state("attack")
    elif bat.default_pos.distance_squared_to(bat.pos) >= 9:
        bat.set_state("fly")
        vector_dir = (bat.default_pos - bat.pos).normalize()
        bat.velocity = vector_dir * BASE_SPEED
        bat.flipped = True if vector_dir.x < 0 else False
    else:
        bat.velocity.x = 0
        bat.velocity.y = 0
        bat.set_state("fly")
