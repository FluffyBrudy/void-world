import sys
import re
import pygame
from pathlib import Path
from typing import Dict, Sequence, Tuple, Union


def load_image(
    path: Path,
    scale_ratio_or_size: Union[Tuple[float, float], float] = 1.0,
    colorkey=None,
):
    if not path.exists():
        print(f"[WARNING]: {path} not found")
        sys.exit(1)

    image = pygame.image.load(path).convert_alpha()
    if colorkey:
        image.set_colorkey(colorkey)

    if type(scale_ratio_or_size) == float or type(scale_ratio_or_size) == int:
        scaled_image = pygame.transform.scale_by(image, scale_ratio_or_size)
        return scaled_image
    elif len(scale_ratio_or_size) > 1:  # type:ignore
        scaled_image = pygame.transform.scale(image, scale_ratio_or_size)  # type: ignore
        return scaled_image
    else:
        print(f"[WARNING]: invalid scale-ratio or size")
        sys.exit(1)


def load_images(dir_path: Path, scale: Union[Tuple[float, float], float] = 1):
    if not dir_path.exists():
        print(f"[WARNING]: directory {dir_path} not found")
        sys.exit(1)
    sorted_path = sorted(
        [path for path in dir_path.iterdir() if path.suffix == ".png"],
        key=get_numeric_sort_key,
    )
    return [load_image(img, scale) for img in sorted_path]


def load_key_images(
    dir_path: Path,
    scale: Union[Tuple[float, float], float] = 1,
    key_index: Union[Sequence[int], Tuple[int]] = (0,),
    /,
):
    if not dir_path.exists():
        print(f"[WARNING]: directory {dir_path} not found")
        sys.exit(1)
    sorted_path = sorted(
        [path for path in dir_path.iterdir() if path.suffix == ".png"],
        key=get_numeric_sort_key,
    )
    st_index = key_index[0]
    end_index = max(st_index + 1, len(key_index) - 1)

    res: Dict[str, pygame.Surface] = {}
    for img in sorted_path:
        key = img.stem[st_index : end_index + 1]
        if len(key) > 1 and key[0] == "0":
            key = key[1 : len(key)]
        value = load_image(img, scale)
        res[key] = value
    return res


def get_numeric_sort_key(filepath: Union[Path, str]) -> Tuple[float, str]:
    if isinstance(filepath, Path):
        filepath = str(filepath)

    match = re.search(r"\d+", filepath)
    number = int(match.group()) if match else float("inf")

    return (number, filepath)
