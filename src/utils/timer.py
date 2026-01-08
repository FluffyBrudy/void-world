from typing import Union

import pygame

from pydebug import pgdebug


class Timer:
    """
    Args:
            interval (float): milisecond time interval
    """

    __slots__ = ("interval", "start_timer")

    def __init__(self, interval: Union[float, int]) -> None:
        self.start_timer = pygame.time.get_ticks() - (interval - 1)
        self.interval = interval

    def reset_to_now(self):
        self.start_timer = pygame.time.get_ticks()

    def has_reach_interval(self):
        return (pygame.time.get_ticks() - self.start_timer) >= self.interval

    def has_reached(self, interval_ratio: float):
        if 0 >= interval_ratio >= 1.0:
            print(
                "[WARNING]: interval_ratio must be withing inclusive range of 0 and 1.0"
            )
            return None
        return (pygame.time.get_ticks() - self.start_timer) >= int(
            self.interval * interval_ratio
        )
