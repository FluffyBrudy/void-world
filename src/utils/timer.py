from typing import Union

import pygame

from logger import logger


class Timer:
    """
    Args:
            interval (float): milisecond time interval
    """

    __slots__ = ("interval", "start_timer")

    def __init__(self, interval: Union[float, int], stale_init=False) -> None:
        self.start_timer = pygame.time.get_ticks()
        if stale_init:
            self.start_timer -= interval - 1
        self.interval = int(interval)

    def reset_to_now(self):
        self.start_timer = pygame.time.get_ticks()

    def has_reached_interval(self):
        return (pygame.time.get_ticks() - self.start_timer) >= self.interval

    def has_reached(self, interval_ratio: float):
        if 0 >= interval_ratio >= 1.0:
            logger.warning("interval_ratio must be within inclusive range of 0 and 1.0")
            return None
        return (pygame.time.get_ticks() - self.start_timer) >= int(self.interval * interval_ratio)

    def stale(self):
        if self.interval > 0:
            self.start_timer -= self.interval - 1
