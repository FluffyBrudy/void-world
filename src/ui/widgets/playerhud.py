from typing import TYPE_CHECKING

from pygame.surface import Surface

from constants import SCREEN_HEIGHT, SCREEN_WIDTH
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
    "background": (155, 193, 217, 200),
    "border_color": (255, 255, 255, 255),
    "border_width": 5,
    "border_radius": 10,
    "margin_x": int((SCREEN_WIDTH - SCREEN_WIDTH * 0.4) // 2),
    "margin_y": SCREEN_HEIGHT - 2 * (SCREEN_HEIGHT // 10),
    "padding_x": 5,
    "padding_y": 5,
    "width": int(SCREEN_WIDTH * 0.4),
    "height": SCREEN_HEIGHT // 10,
}


class PlayerHUD(UIBase):
    game: "Game" = None  # type: ignore

    def __init__(self, player: "Player") -> None:
        super().__init__(HUD_MAIN_UIOPTIONS)

        HUD_PAD_X = 10
        HUD_PAD_Y = 8
        BAR_HEIGHT = 24
        BAR_SPACING = 6
        SKILL_SIZE = 56
        SKILL_SPACING = 8

        content_w = self.box_model["content_width"]
        content_h = self.box_model["content_height"]

        bar_width = int(content_w * 0.45)

        self.healthbar = ProgressBarUI(
            width=bar_width,
            height=BAR_HEIGHT,
            margin_x=HUD_PAD_X,
            margin_y=HUD_PAD_Y,
            fill_color="lime",
        )

        self.manabar = ProgressBarUI(
            width=bar_width,
            height=BAR_HEIGHT,
            margin_x=HUD_PAD_X,
            margin_y=HUD_PAD_Y + BAR_HEIGHT + BAR_SPACING,
            fill_color="skyblue",
        )

        skills_y = content_h // 2 - SKILL_SIZE // 2
        skills_start_x = content_w - HUD_PAD_X - (SKILL_SIZE * 2) - SKILL_SPACING

        self.dash_cooldown_ui = CooldownOverlay(
            skill=player.skills["dash"],
            icon=self.game.icons["player/skills"]["dash"],
            size=SKILL_SIZE,
            **{**SKILLS_DEFAULT_UIOPTIONS, "margin_x": skills_start_x, "margin_y": skills_y},
        )

        self.heal_cooldown_ui = CooldownOverlay(
            skill=player.skills["heal"],
            icon=self.game.icons["player/skills"]["heal"],
            size=SKILL_SIZE,
            **{
                **SKILLS_DEFAULT_UIOPTIONS,
                "margin_x": skills_start_x + SKILL_SIZE + SKILL_SPACING,
                "margin_y": skills_y,
            },
        )

        self.add_plugin(self.healthbar.render)
        self.add_plugin(self.manabar.render)
        self.add_plugin(self.dash_cooldown_ui.render)
        self.add_plugin(self.heal_cooldown_ui.render)

        self.player = player

    def render(self, screen: Surface):
        super().render(screen)

    def update(self):
        self.healthbar.set_progress(self.player.stats["health"])
        self.manabar.set_progress(self.player.stats["mana"])
        self.healthbar.update()
        self.manabar.update()
