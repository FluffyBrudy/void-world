from typing import Callable, Unpack, cast, override

from pygame.math import Vector2
from pygame.rect import Rect
from pygame.surface import Surface

from ttypes.index_type import Rectable, TPosType, UIOptions
from ui.widgets.progressbar import ProgressBarUI
from utils.timer import Timer


class HealthbarUI(ProgressBarUI):
    def __init__(self, entity: object, visibility_timer=2000, **overrides: Unpack[UIOptions]) -> None:
        """rectable instance is any class that has either hitbox method or rect method
        that returns Rect object
        """

        if getattr(entity, "hitbox") is not None:
            self.rect = entity.hitbox  # type: ignore
        elif getattr(entity, "rect", None) is not None:
            self.rect = entity.rect  # type: ignore
        else:
            raise TypeError("entity must support hitbox or rect method")

        super().__init__(**overrides)

        self.rect = cast(Callable[[], Rect], self.rect)
        self.entity = cast(Rectable, entity)
        self.visibility_timer = Timer(visibility_timer)

    def on_alter(self, amount: float, /):
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
