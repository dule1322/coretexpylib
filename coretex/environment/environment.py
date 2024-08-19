from typing import List, Any
from typing_extensions import Self
from abc import ABC, abstractmethod
from pathlib import Path

import shutil
import logging
import subprocess

from .environment_type import EnvironmentType


logger = logging.getLogger(__name__)

MAX_ENVIRONMENT_RETRY_COUNT = 3


class Environment(ABC):

    def __init__(self, path: Path, environmentFile: Path, type_: EnvironmentType) -> None:
        self.path = path
        self.environmentFile = environmentFile
        self.type = type_

    @classmethod
    @abstractmethod
    def create(cls, *args: Any, **kwargs: Any) -> Self:
        pass

    @property
    def name(self) -> str:
        return self.path.name

    @property
    def pip(self) -> Path:
        return self.path.joinpath("bin", "pip")

    @property
    def python(self) -> Path:
        return self.path.joinpath("bin", "python")

    @property
    def exists(self) -> bool:
        return self.path.exists()

    def cleanCache(self) -> None:
        pass

    @abstractmethod
    def getCreationArgs(self) -> List[str]:
        pass

    @abstractmethod
    def getInstallationArgs(self, packages: List[str]) -> List[str]:
        pass

    @abstractmethod
    def getActivationArgs(self) -> List[str]:
        pass

    def delete(self) -> None:
        shutil.rmtree(self.path)

    def createEnvironment(self, workingDirectory: Path, retryCount: int = 0) -> None:
        logger.info(">> [Coretex] Creating environment")

        # Clean cache to make sure it is always using latest changes
        self.cleanCache()

        args = self.getCreationArgs()
        process = subprocess.run(args, cwd = workingDirectory)

        if process.returncode != 0:
            if self.exists:
                logger.info(f">> [Coretex] Deleting corrupted environment \"{self.path}\"")
                self.delete()

            # If environment creation failed retry up to 3 times
            if retryCount < MAX_ENVIRONMENT_RETRY_COUNT:
                return self.createEnvironment(workingDirectory, retryCount = retryCount + 1)

            raise RuntimeError(f"Failed to create environment. Exit code: {process.returncode}")

    def installPackages(self, packages: List[str], workingDirectory: Path, retryCount: int = 0) -> None:
        logger.info(f">> [Coretex] Installing packages {packages}")

        args = self.getInstallationArgs(packages)
        process = subprocess.run(args, cwd = workingDirectory)

        if process.returncode != 0:
            # If package installation failed retry up to 3 times
            if retryCount < MAX_ENVIRONMENT_RETRY_COUNT:
                return self.installPackages(packages, workingDirectory, retryCount = retryCount + 1)

            raise RuntimeError(f"Failed to install packages {packages}. Exit code: {process.returncode}")
