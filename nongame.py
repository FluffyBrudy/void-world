from PIL import Image
from pathlib import Path


def trim_transparent_pixel(path: Path):
    test_dir = Path("./test_dir")
    test_dir.mkdir(exist_ok=True)
    for file in path.rglob("*/**.png"):
        image = Image.open(file)
        bbox = image.getbbox()
        image = image.crop(bbox)
        subdir = file.parent.name
        dest = test_dir.resolve() / subdir / file.name
        dest.parent.mkdir(exist_ok=True, parents=True)
        image.save(dest)


path = Path.cwd() / "assets" / "Player"
trim_transparent_pixel(path)
