from typing import TYPE_CHECKING

from pygame.surface import Surface

from ttypes.index_type import UIOptions
from ui.base.uibase import UIBase
from ui.elements.progressbar import ProgressBarUI
from ui.widgets.overlay import CooldownOverlay

if TYPE_CHECKING:
    from entities.player import Player
    from game import Game


SKILLS_DEFAULT_UIOPTIONS: UIOptions = {
    "background": (15, 15, 15, 160),
    "border_color": (200, 200, 200, 100),
    "border_width": 2,
    "border_radius": 12,
    "width": 64,
    "height": 64,
    "margin_x": 8,
    "margin_y": 0,
    "padding_x": 4,
    "padding_y": 4,
}
HUD_MAIN_UIOPTIONS: UIOptions = {
    "background": (0, 0, 0, 0),
    "border_color": (255, 255, 255, 0),
    "border_width": 0,
    "border_radius": 0,
    "margin_x": 20,
    "margin_y": 20,
    "padding_x": 10,
    "padding_y": 10,
}


class PlayerHUD(UIBase):
    game: "Game" = None  # type: ignore

    def __init__(self, player: "Player") -> None:
        super().__init__(HUD_MAIN_UIOPTIONS)

        self.dash_cooldown_ui = CooldownOverlay(
            skill=player.skills["dash"],
            icon=self.game.icons["player/skills"]["dash"],
            size=78,
            **SKILLS_DEFAULT_UIOPTIONS,
        )
        self.heal_cooldown_ui = CooldownOverlay(
            skill=player.skills["heal"],
            icon=self.game.icons["player/skills"]["heal"],
            size=78,
            **{**SKILLS_DEFAULT_UIOPTIONS, "margin_y": self.dash_cooldown_ui.box_model["offset_y"]},
        )

        self.healthbar = ProgressBarUI(fill_color="lime")  # type: ignore
        self.healthbar.set_progress(player.stats["health"])
        self.manabar = ProgressBarUI(fill_color="skyblue", margin_y=int(self.healthbar.fullsize[1] * 1.4))  # type: ignore
        self.manabar.set_progress(player.stats["mana"])

        self.player = player

    def render(self, screen: Surface):
        # self.dash_cooldown_ui.render(screen)
        self.heal_cooldown_ui.render(screen)
        self.manabar.render(screen)
        self.healthbar.render(screen)
        return super().render(screen)

    def update(self):
        self.healthbar.set_progress(self.player.stats["health"])
        self.manabar.set_progress(self.player.stats["mana"])
        self.healthbar.update()
        self.manabar.update()
