def melee_range(attacker, target) -> bool:
    return attacker.rect().colliderect(target.hitbox())


def horizontal_range(attacker, target, *, max_x: int, max_y: int) -> bool:
    dx = abs(target.pos.x - attacker.pos.x)
    dy = abs(target.pos.y - attacker.pos.y)
    return dx <= max_x and dy <= max_y


def radial_range(attacker, target, radius: int) -> bool:
    dx = target.pos.x - attacker.pos.x
    dy = target.pos.y - attacker.pos.y
    return dx * dx + dy * dy <= radius * radius
