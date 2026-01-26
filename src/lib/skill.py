from typing import TYPE_CHECKING

from utils.timer import Timer

if TYPE_CHECKING:
    from entities.base_entity import BaseEntity


class Skill:
    def __init__(self, *, mana_cost: float, cooldown: float, damage: float = 0.0, health_regain: float = 0.0) -> None:
        self.mana_cost = mana_cost
        self.damage = damage
        self.health_regain = health_regain
        self.cooldown_timer = Timer(cooldown, stale_init=True)
        self.active = True

    def can_use(self, entity: "BaseEntity"):
        return entity.stats["mana"] >= self.mana_cost and self.cooldown_timer.has_reached_interval()

    def consume(self, entity: "BaseEntity"):
        entity.stats["mana"] = max(0, entity.stats["mana"] - self.mana_cost)
        self.cooldown_timer.reset_to_now()
