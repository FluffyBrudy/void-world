from typing import List, Tuple

from pygame import Surface, Vector2


class DashEffect:
    frame_limits = 10
    temp_frames: List[Surface] = []

    @classmethod
    def add_frame(cls, frame: Surface):
        if len(cls.temp_frames) > DashEffect.frame_limits:
            cls.temp_frames.pop(0)
        cls.temp_frames.append(frame)

    @classmethod
    def render(
        cls, surface: Surface, pos_with_offset: Tuple[int, int] | Vector2, direction=1
    ):
        total_frames = len(cls.temp_frames)
        for i, frame in enumerate(cls.temp_frames, start=0):
            frame.set_alpha(100)
            pos = (
                pos_with_offset[0] + direction * (total_frames - i) * 30,
                pos_with_offset[1],
            )
            surface.blit(frame, pos)

    @classmethod
    def clear(cls):
        cls.temp_frames = []
