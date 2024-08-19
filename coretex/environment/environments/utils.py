from typing import List
from pathlib import Path

import os
import hashlib
import shutil


def cleanWhitespace(value: str) -> str:
    return "".join(value.split())


def loadMultipleFiles(paths: List[Path]) -> List[str]:
    paths.sort()

    lines: List[str] = []

    for path in paths:
        with path.open("r") as file:
            lines.extend(file.readlines())

    return lines


def hashPathContent(paths: List[Path]) -> str:
    lines = loadMultipleFiles(paths)
    lines = [cleanWhitespace(line) for line in lines]
    lines.sort()

    fileContent = "".join(lines)
    hash = hashlib.sha256(fileContent.encode("UTF-8"))

    return hash.digest().hex()


def cleanCondaPkgs(condaPath: Path) -> None:
    condaPkgsPath = condaPath / "pkgs"
    if not condaPkgsPath.exists():
        return

    for path in condaPkgsPath.iterdir():
        if path.is_file():
            path.unlink()
        else:
            shutil.rmtree(path)


def shell() -> str:
    return Path(os.environ["SHELL"]).stem
