from typing import Optional
from pathlib import Path

import os
import sys
import logging

from .environment import Environment
from .environment_type import EnvironmentType
from .environments import Venv, Conda


logger = logging.getLogger(__name__)


VENV_ENV_FILE_NAME = "requirements.txt"
CONDA_ENV_FILE_NAME_LINUX = "environment.yml"
CONDA_ENV_FILE_NAME_OSX = "environment-osx.yml"


def getCondaEnvironmentFile(operatingSystem: str) -> str:
    if operatingSystem.startswith("linux"):
        return CONDA_ENV_FILE_NAME_LINUX

    if operatingSystem.startswith("darwin"):
        return CONDA_ENV_FILE_NAME_OSX

    raise ValueError(f"{operatingSystem} platform not supported")


def getCondaPath() -> Path:
    if "CTX_BASE_CONDA_ENV_PATH" in os.environ:
        return Path(os.environ["CTX_BASE_CONDA_ENV_PATH"]).expanduser()

    defaultCondaPath = Path.home().joinpath(".miniconda")
    if defaultCondaPath.exists():
        return defaultCondaPath

    raise FileNotFoundError("Conda installation directory not found")


def getTaskEnvironmentType(taskPath: Path, entryPoint: str) -> Optional[EnvironmentType]:
    if taskPath.joinpath(getCondaEnvironmentFile(sys.platform)).exists():
        if entryPoint.endswith(".py") or entryPoint.endswith(".ipynb"):
            return EnvironmentType.conda

        return EnvironmentType.conda

    if taskPath.joinpath(VENV_ENV_FILE_NAME).exists():
        return EnvironmentType.venv

    return None


def create(taskPath: Path, entryPoint: str) -> Optional[Environment]:
    environmentType = getTaskEnvironmentType(taskPath, entryPoint)
    if environmentType is None:
        return None

    logger.info(f">> [Coretex] Using \"{environmentType.name}\" environment")

    if environmentType == EnvironmentType.venv:
        return Venv.create(taskPath / VENV_ENV_FILE_NAME)

    if environmentType == EnvironmentType.conda:
        return Conda.create(taskPath / getCondaEnvironmentFile(sys.platform), getCondaPath())
