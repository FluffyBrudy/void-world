import pygame


class Timer:
    __slots__ = ("interval", "start_time")

    def __init__(self, interval: float):
        self.interval = interval
        self.start_time = pygame.time.get_ticks()

    @property
    def interval_reached(self):
        return (pygame.time.get_ticks() - self.start_time) >= self.interval_reached

    def reset(self):
        self.start_time = pygame.time.get_ticks()
