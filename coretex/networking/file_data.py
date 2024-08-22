#     Copyright (C) 2023  Coretex LLC

#     This file is part of Coretex.ai

#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU Affero General Public License as
#     published by the Free Software Foundation, either version 3 of the
#     License, or (at your option) any later version.

#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.

#     You should have received a copy of the GNU Affero General Public License
#     along with this program.  If not, see <https://www.gnu.org/licenses/>.

from typing import Optional, Union, BinaryIO, Tuple
from typing_extensions import Self
from pathlib import Path
from dataclasses import dataclass
from contextlib import ExitStack

from ..utils import guessMimeType


@dataclass
class FileDescriptor:

    paramName: str
    fileName: str
    data: Union[Path, bytes]
    mimeType: str
    length: int

    @classmethod
    def fromBytes(cls, paramName: str, fileName: str, data: bytes, mimeType: Optional[str] = None) -> Self:
        if mimeType is None:
            mimeType = "application/octet-stream"

        return cls(paramName, fileName, data, mimeType, len(data))

    @classmethod
    def fromPath(cls, paramName: str, path: Union[Path, str], fileName: Optional[str] = None, mimeType: Optional[str] = None) -> Self:
        if isinstance(path, str):
            path = Path(path)

        if not path.exists():
            raise FileNotFoundError(path)

        if not path.is_file():
            raise ValueError(f"{path} is not a file")

        if fileName is None:
            fileName = path.name

        if mimeType is None:
            mimeType = guessMimeType(path)

        return cls(paramName, fileName, path, mimeType, path.stat().st_size)

    def prepareForUpload(self, exitStack: Optional[ExitStack] = None) -> Tuple[str, Tuple[str, Union[bytes, BinaryIO], str]]:
        if isinstance(self.data, Path) and exitStack is None:
            raise ValueError("exitStack must be provided if FileDescriptor.data is Path")

        if isinstance(self.data, Path):
            # exitStack cannot be None at this point, but mypy disagrees
            data = exitStack.enter_context(self.data.open("rb"))  # type: ignore[union-attr]
        else:
            data = self.data

        return self.paramName, (self.fileName, data, self.mimeType)
