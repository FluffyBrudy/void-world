from typing import Callable, Unpack, cast, override

from pygame.math import Vector2
from pygame.rect import Rect
from pygame.surface import Surface

from ttypes.index_type import HasHitbox, HasRect, TPosType, UIOptions
from ui.widgets.progressbar import ProgressBarUI
from utils.timer import Timer


class HealthbarUI(ProgressBarUI):
    def __init__(self, rectabel_instance: HasRect | HasHitbox, **overrides: Unpack[UIOptions]) -> None:
        """rectable instance is any class that has either hitbox method or rect method
        that returns Rect object
        """

        super().__init__(**overrides)
        rect = getattr(rectabel_instance, "hitbox", getattr(rectabel_instance, "rect", None))
        if rect is None:
            raise AttributeError("rectable instance must have either hitbox ")
        self.rect = cast(Callable[[], Rect], rect)

        self.visibility_timer = Timer(2000)

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
