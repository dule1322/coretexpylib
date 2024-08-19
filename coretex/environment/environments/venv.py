from typing import List
from typing_extensions import Self
from pathlib import Path

from coretex import folder_manager

from . import utils
from ..environment import Environment
from ..environment_type import EnvironmentType


class Venv(Environment):

    def __init__(self, path: Path, environmentFile: Path) -> None:
        super().__init__(path, environmentFile, EnvironmentType.venv)

    @classmethod
    def create(cls, environmentFile: Path) -> Self:
        environmentName = utils.hashPathContent([environmentFile])
        environmentPath = folder_manager.environments / environmentName

        return cls(environmentPath, environmentFile)

    @property
    def _executable(self) -> str:
        return "python"

    def getCreationArgs(self) -> List[str]:
        return [
            # Version hardcoded for now
            "python", "-m", "venv", str(self.path),

            "&&",

            # Ignore cache when installing dependencies
            str(self.pip), "install", "-r", str(self.environmentFile), "--no-cache-dir"
        ]

    def getInstallationArgs(self, packages: List[str]) -> List[str]:
        return [ str(self.pip), "install" ] + packages + [ "--no-cache-dir" ]

    def getActivationArgs(self) -> List[str]:
        activationScript = self.path.joinpath("bin", "activate")
        return [ ".", str(activationScript) ]
