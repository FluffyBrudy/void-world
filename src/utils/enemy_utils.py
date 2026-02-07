from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.entities.base_entity import BaseEntity


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
