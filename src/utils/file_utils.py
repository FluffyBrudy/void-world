from pathlib import Path
import re
from typing import Dict, List
import shutil


def classify_and_move_files(dir_path: Path) -> Dict[str, List[Path]]:
    prefix_map: Dict[str, List[Path]] = {}

    for file in dir_path.iterdir():
        if file.is_file():
            match = re.match(r"[a-zA-Z]+", file.stem)
            if match:
                prefix = match.group()
                prefix_folder = dir_path / prefix
                prefix_folder.mkdir(exist_ok=True)
                destination = prefix_folder / file.name
                shutil.move(str(file), destination)
                prefix_map.setdefault(prefix, []).append(destination)

    return prefix_map


if __name__ == "__main__":
    dir_to_scan = Path("/home/rudy/Documents/games/void-world/assets/enemies/Enemy05")
    classified = classify_and_move_files(dir_to_scan)

    for prefix, files in classified.items():
        print(f"Prefix '{prefix}' has {len(files)} file(s):")
        for f in files:
            print(f"  - {f}")
