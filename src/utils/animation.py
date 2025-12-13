from typing import Sequence
from pygame import Surface


class Animation:
    __slots__ = ("frames", "frames_len", "loop", "frame_index", "animation_speed")

    def __init__(
        self, frames: Sequence[Surface], animation_speed=0.1, loop=True
    ) -> None:
        self.loop = loop
        self.frame_index = 0
        self.frames = frames
        self.frames_len = len(frames)
        self.animation_speed = animation_speed

    def copy(self):
        return Animation(
            self.frames, animation_speed=self.animation_speed, loop=self.loop
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
        self.frame_index += self.animation_speed
        if self.has_animation_end():
            if self.loop:
                self.reset_animation()
            else:
                self.frame_index = self.frames_len

    def has_animation_end(self):
        return self.frame_index >= self.frames_len

    def reset_animation(self):
        self.frame_index = 0
