from typing import Optional, Sequence, override
from pygame import Surface


class Animation:
    # __slots__ = ("frames", "frames_len", "loop", "frame_index", "animation_speed")

    def __init__(
        self, frames: Sequence[Surface], animation_speed=0.1, loop=True
    ) -> None:
        self.loop = loop
        self.frame_index = 0
        self.frames = frames
        self.frames_len = len(frames)
        self.animation_speed = animation_speed

    def copy(self):
        return self.__class__(
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

    def force_change_frames(
        self, frames: Sequence[Surface], animation_speed: Optional[float] = None
    ):
        if animation_speed is not None:
            self.animation_speed = animation_speed
        self.frames = frames
        self.frames_len = len(self.frames)


class PostAnimatableAnimation(Animation):
    # __slots__ = ("post_frames", "__reshaped", "loop")

    def __init__(
        self,
        post_frames: Sequence[Surface],
        frames: Sequence[Surface],
        post_animation_speed: float,
        animation_speed=0.1,
        loop=True,
    ) -> None:
        super().__init__(frames, animation_speed, loop)
        self.post_animation_speed = post_animation_speed
        self.post_frames = post_frames
        self.__reshaped = False

    def will_end(self):
        """important to call since has_animation_end is not stable for this due to mutation on update method"""
        return self.frame_index + self.animation_speed >= self.frames_len

    @override
    def update(self):
        if not self.__reshaped and self.will_end():
            self.__reshaped = True
            self.force_change_frames(self.post_frames, self.post_animation_speed)
            self.loop = self.loop
        super().update()

    @override
    def copy(self):
        return PostAnimatableAnimation(
            post_frames=self.post_frames,
            frames=self.frames,
            animation_speed=self.animation_speed,
            post_animation_speed=self.post_animation_speed,
            loop=self.loop,
        )
