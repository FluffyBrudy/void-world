import sys
import re
import pygame
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Tuple, TypedDict, Union, Unpack

from logger import logger
from ttypes.index_type import ImageLoadOptions


def load_image(path: Path, /, **options: Unpack[ImageLoadOptions]) -> pygame.Surface:
    if not path.exists():
        logger.warning(f"{path} not found")
        sys.exit(1)

    image = pygame.image.load(path).convert_alpha()
    return apply_image_options(image, **options)


def load_spritesheet(
    path: Path, frame_size: Tuple[int, int], /, **options: Unpack[ImageLoadOptions]
):
    if not path.exists():
        logger.warning(f"{path} not found")
        sys.exit(1)

    spritesheet = pygame.image.load(path).convert_alpha()
    if (spritesheet.width % frame_size[0]) != 0:
        logger.warning("width isn't symmetric")
        sys.exit(1)
    if (spritesheet.height % frame_size[1]) != 0:
        logger.warning("height isn't symmetric")
        sys.exit(1)

    row_len = spritesheet.height // frame_size[1]
    col_len = spritesheet.width // frame_size[0]

    frames: List[pygame.Surface] = []
    for row in range(row_len):
        y_pos = row * frame_size[1]
        for col in range(col_len):
            topleft = (col * frame_size[0], y_pos)
            frames.append(
                apply_image_options(
                    spritesheet.subsurface((topleft, frame_size)), **options
                )
            )

    return frames


def load_images(
    dir_path: Path,
    /,
    **options: Unpack[ImageLoadOptions],
):
    if not dir_path.exists():
        logger.warning(f"directory {dir_path} not found")
        sys.exit(1)

    sorted_paths = sorted(
        (p for p in dir_path.iterdir() if p.suffix == ".png"),
        key=get_numeric_sort_key,
    )

    return [load_image(path, **options) for path in sorted_paths]


def load_key_images(
    dir_path: Path,
    key_index: Sequence[int] = (0,),
    /,
    **options: Unpack[ImageLoadOptions],
):
    if not dir_path.exists():
        logger.warning(f"directory {dir_path} not found")
        sys.exit(1)

    sorted_paths = sorted(
        (p for p in dir_path.iterdir() if p.suffix == ".png"),
        key=get_numeric_sort_key,
    )

    st_index = key_index[0]
    end_index = max(st_index + 1, len(key_index) - 1)

    res: Dict[str, pygame.Surface] = {}
    for img in sorted_paths:
        key = img.stem[st_index : end_index + 1]
        if len(key) > 1 and key.startswith("0"):
            key = key[1:]

        res[key] = load_image(img, **options)

    return res


def apply_image_options(
    image: pygame.Surface, /, **options: Unpack[ImageLoadOptions]
) -> pygame.Surface:
    colorkey = options.get("colorkey")
    if colorkey is not None:
        image.set_colorkey(colorkey)

    to_trim, trim_area = options.get("trim_transparent_pixel", (False, None))
    if to_trim:
        if trim_area is None:
            image = image.subsurface(image.get_bounding_rect())
        else:
            image = image.subsurface(trim_area)

    flip_x, flip_y = options.get("flip", (False, False))
    if flip_x or flip_y:
        image = pygame.transform.flip(image, flip_x, flip_y)

    scale = options.get("scale_ratio_or_size")
    if scale is not None:
        if isinstance(scale, (int, float)):
            image = pygame.transform.scale_by(image, scale)
        elif isinstance(scale, tuple) and len(scale) == 2:
            image = pygame.transform.scale(image, scale)
        else:
            logger.warning("invalid scale_ratio_or_size")
            sys.exit(1)

    return image


def get_numeric_sort_key(filepath: Union[Path, str]) -> Tuple[float, str]:
    if isinstance(filepath, Path):
        filepath = str(filepath)

    match = re.search(r"\d+", filepath)
    number = int(match.group()) if match else float("inf")

    return (number, filepath)
