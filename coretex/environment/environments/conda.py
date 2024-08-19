from typing import List
from typing_extensions import Self
from pathlib import Path

import sys

from coretex import folder_manager

from .utils import hashPathContent, shell, cleanCondaPkgs
from ..environment import Environment
from ..environment_type import EnvironmentType


class Conda(Environment):

    def __init__(self, path: Path, environmentFile: Path, condaPath: Path) -> None:
        super().__init__(path, environmentFile, EnvironmentType.conda)

        self.condaPath = condaPath

    @classmethod
    def create(cls, environmentFile: Path, condaPath: Path) -> Self:
        requirementsPath = environmentFile.parent / "requirements.txt"
        if requirementsPath.exists():
            environmentName = hashPathContent([environmentFile, requirementsPath])
        else:
            environmentName = hashPathContent([environmentFile])

        environmentPath = folder_manager.environments / environmentName
        return cls(environmentPath, environmentFile, condaPath)

    def cleanCache(self) -> None:
        cleanCondaPkgs(self.condaPath)

    def getCreationArgs(self) -> List[str]:
        return [
            # Step 1: Clean conda cache
            "yes", "|", "conda", "clean", "--all",

            "&&"

            # Step 2: Create conda environment
            "conda", "env", "create",
            "--prefix", str(self.path),
            "--file", str(self.environmentFile)
        ]

    def getInstallationArgs(self, packages: List[str]) -> List[str]:
        installationArgs = [
            "yes", "|", "conda", "install",
            "--prefix", str(self.path)
        ]

        return installationArgs + packages + [ "-c", "conda-forge" ]

    def getActivationArgs(self) -> List[str]:
        condaActivatePath = self.condaPath / "bin" / "activate"

        initCondaArgs = [
            # Step 1: Activate base conda environment
            ".", str(condaActivatePath),

            "&&",

            # Step 2: Initialize conda
            "conda", "init", shell(),
        ]

        # Known issue on macOS systems
        # Reference: https://github.com/conda/conda/issues/10401
        if "darwin" in sys.platform:
            initCondaArgs.extend([ "&&", "conda", "deactivate" ])

        return initCondaArgs + [
            "&&",

            # Step 3: Activate conda environment
            "conda", "activate", str(self.path),
        ]
