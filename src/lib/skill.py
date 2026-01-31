from typing import TYPE_CHECKING

from utils.timer import Timer

if TYPE_CHECKING:
    from entities.base_entity import BaseEntity


class Skill:
    def __init__(self, *, costs: dict[str, float], effects: dict[str, float], cooldown: float) -> None:
        self.costs = costs
        self.effects = effects
        self.cooldown_timer = Timer(cooldown, stale_init=True)

    def can_use(self, entity: "BaseEntity") -> bool:
        can_afford = all(entity.stats.get(s, 0) >= v for s, v in self.costs.items())
        return can_afford and self.cooldown_timer.has_reached_interval()

    def apply(self, entity: "BaseEntity"):
        for stat, value in self.costs.items():
            entity.modify_stat(stat, -value)

        for stat, value in self.effects.items():
            entity.modify_stat(stat, value)

        self.cooldown_timer.reset_to_now()
