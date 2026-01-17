from typing import Optional, Tuple, TypedDict
from pygame.typing import ColorLike, Point, RectLike


class ImageLoadOptions(TypedDict, total=False):
    scale_ratio_or_size: Tuple[int, int] | Tuple[float, float] | float | int
    trim_transparent_pixel: Tuple[bool, RectLike | None]
    flip: Tuple[bool, bool]
    colorkey: Optional[ColorLike]


class BoxModel(TypedDict, total=True):
    margin_x: int
    margin_y: int
    padding_x: int
    padding_y: int
    width: int
    height: int
    border_width: int


class BoxModelResult(TypedDict, total=True):
    left: int
    top: int
    offset_x: int
    offset_y: int
    full_width: int
    full_height: int
    content_width: int
    content_height: int


class UIOptions(BoxModel, total=False):
    border_radius: int
    border_color: ColorLike
    background: ColorLike
