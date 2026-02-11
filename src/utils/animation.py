from typing import Sequence

from pygame import Surface


class Animation:
    # __slots__ = ("frames", "frames_len", "loop", "frame_index", "animation_speed")

    def __init__(self, name: str, frames: Sequence[Surface], animation_speed=0.1, loop=True) -> None:
        self.name = name
        self.loop = loop
        self.frame_index = 0
        self.frames = frames
        self.frames_len = len(frames)
        self.animation_speed = animation_speed

        self.__locked = False

    def copy(self):
        return self.__class__(
            name=self.name,
            frames=self.frames,
            animation_speed=self.animation_speed,
            loop=self.loop,
        )

    def get_frame(self):
        animation_ended = self.has_animation_end()
        if animation_ended:
            if not self.loop:
                return self.frames[self.frames_len - 1]
            else:
                return self.frames[0]
        return self.frames[int(self.frame_index)]

    def update(self):
        if self.__locked:
            return
        self.frame_index = round(self.frame_index + self.animation_speed, 2)
        if self.has_animation_end():
            if self.loop:
                self.reset_animation()
            else:
                self.frame_index = self.frames_len

    def has_animation_end(self):
        return self.frame_index >= self.frames_len

    def reset_animation(self):
        self.frame_index = 0

    def lock(self):
        self.__locked = True

    def release_lock(self):
        self.__locked = False

    @property
    def is_locked(self):
        return self.__locked

    def safe_frame_index(self):
        return int(self.frame_index) % len(self.frames)
