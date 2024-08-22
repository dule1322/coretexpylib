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

from typing import Union, Iterator, Tuple
from pathlib import Path

import logging

from .network_manager_base import FileDescriptor
from .network_manager import networkManager
from .network_response import NetworkRequestError


MAX_CHUNK_SIZE = 128 * 1024 * 1024  # 128 MiB


def initiateChunkUploadSession(path: Path) -> str:
    parameters = {
        "size": path.stat().st_size
    }

    response = networkManager.post("upload/start", parameters)
    if response.hasFailed():
        raise NetworkRequestError(response, f"Failed to initiate chunk upload session for \"{path}\"")

    uploadId = response.getJson(dict).get("id")

    if not isinstance(uploadId, str):
        raise TypeError(f">> [Coretex] Field \"id\" is of tpye")

    return uploadId


def chunks(path: Path, chunkSize: int) -> Iterator[Tuple[int, int, bytes]]:
    with path.open("rb") as file:
        while True:
            # Position before read is start
            start = file.tell()

            # Read the chunk
            chunk = file.read(chunkSize)

            # Read until there are no more bytes
            if not chunk:
                break

            # Position after the read is end
            end = file.tell()

            yield start, end, chunk


def uploadChunk(sessionId: str, fileName: str, start: int, end: int, data: bytes) -> None:
    parameters = {
        "id": sessionId,
        "start": start,
        "end": end - 1  # API expects start/end to be inclusive
    }

    files = [
        FileDescriptor.fromBytes("file", fileName, data)
    ]

    response = networkManager.formData("upload/chunk", parameters, files)
    if response.hasFailed():
        raise NetworkRequestError(response, f"Failed to upload file chunk with byte range \"{start}-{end}\"")

    logging.getLogger("coretexpylib").debug(f">> [Coretex] Uploaded chunk with range \"{start}-{end}\"")


def fileChunkUpload(path: Union[Path, str], chunkSize: int = MAX_CHUNK_SIZE) -> str:
    """
        Uploads file in chunks to Coretex.ai server.
        Should be used when uploading files larger than 128 MiB.

        Parameters
        ----------
        path : Path
            File which will be uploaded in chunks
        chunkSize : int
            Size of the chunks into which file will be split
            before uploading. Maximum value is 128 MiBs.

        Returns
        -------
        str -> id of the file which was uploaded
    """

    if isinstance(path, str):
        path = Path(path)

    if not path.exists():
        raise FileNotFoundError(path)

    if not path.is_file():
        raise ValueError(f"{path} is not a file")

    if chunkSize > MAX_CHUNK_SIZE:
        chunkSize = MAX_CHUNK_SIZE

    sessionId = initiateChunkUploadSession(path)

    for start, end, chunk in chunks(path, chunkSize):
        uploadChunk(sessionId, path.name, start, end, chunk)

    return sessionId
