from typing import TYPE_CHECKING

from pygame import Vector2

from ttypes.index_type import VectorPos
from utils.math_utils import sign

if TYPE_CHECKING:
    from entities.base_entity import BaseEntity


def melee_range(attacker: "BaseEntity", target: "BaseEntity") -> bool:
    return attacker.rect().colliderect(target.hitbox())


def horizontal_range(attacker: "BaseEntity", target: "BaseEntity", *, max_x: int, max_y: int) -> bool:
    dx = abs(target.pos.x - attacker.pos.x)
    dy = abs(target.pos.y - attacker.pos.y)
    return dx <= max_x and dy <= max_y


def radial_range(attacker: "BaseEntity", target: "BaseEntity", radius: int) -> bool:
    dx = target.pos.x - attacker.pos.x
    dy = target.pos.y - attacker.pos.y
    return dx * dx + dy * dy <= radius * radius


def direction(a: VectorPos, b: VectorPos, *, normalize: bool = False, scale=1.0):
    if normalize:
        return (b.pos - a.pos).normalize() * scale
    return Vector2(sign(b.pos.x - a.pos.x), sign(b.pos.y - a.pos.y)) * scale
