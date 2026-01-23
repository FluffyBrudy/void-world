from typing import Unpack, override

from pygame.math import Vector2
from pygame.surface import Surface

from lib.eventbus import event_bus
from ttypes.index_type import DamagableEntity, TPosType, UIOptions
from ui.widgets.progressbar import ProgressBarUI
from utils.timer import Timer


class HealthbarUI(ProgressBarUI):
    def __init__(self, entity: "DamagableEntity", **overrides: Unpack[UIOptions]) -> None:
        """rectable instance is any class that has either hitbox method or rect method
        that returns Rect object
        """

        super().__init__(**overrides)

        self.entity = entity
        self.rect = entity.hitbox

        self.visibility_timer = Timer(2000)
        event_bus.subscribe("enemy_damaged", self._on_alter)

    def _on_alter(self, *, entity: "DamagableEntity", amount: float):
        if entity != self.entity:
            return

        self.set_health(amount)
        self.trigger_visibility()

    def set_health(self, health: float):
        self.set_progress(health)

    def get_health(self):
        return self.get_progress()

    def trigger_visibility(self):
        self.visibility_timer.reset_to_now()

    @override
    def render(self, screen: Surface, pos_offset: TPosType):  # type: ignore
        if self.visibility_timer.has_reached_interval():
            return
        fullsize = self.fullsize
        rect = self.rect()
        pos = (
            rect.left - (fullsize[0] - rect.w) // 2,
            rect.top - (2 * fullsize[1]),
        )
        super().render(screen, pos - Vector2(pos_offset))
