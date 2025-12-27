from typing import Optional, Tuple, TypedDict
from pygame.typing import ColorLike, Point, RectLike


class ImageLoadOptions(TypedDict, total=False):
    scale_ratio_or_size: Tuple[int, int] | Tuple[float, float] | float | int
    trim_transparent_pixel: Tuple[bool, RectLike | None]
    flip: Tuple[bool, bool]
    colorkey: Optional[ColorLike]
