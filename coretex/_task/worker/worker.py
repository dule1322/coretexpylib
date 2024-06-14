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

from typing import Optional, Type
from typing_extensions import Self
from types import TracebackType
from pathlib import Path

import time
import logging
import threading

from . import metrics, artifacts
from ...entities import TaskRun
from ...networking import NetworkRequestError
from ...utils.misc import measure


UPDATE_INTERVAL = 5  # seconds


class TaskRunWorker(threading.Thread):

    def __init__(self, taskRun: TaskRun) -> None:
        super().__init__(daemon = True, name = f"task-run-worker-{taskRun.id}")

        self.taskRun = taskRun

        self._stopFlag = threading.Event()
        self._killFlag = threading.Event()

    @property
    def isStopped(self) -> bool:
        return self._stopFlag.is_set()

    @property
    def isKilled(self) -> bool:
        return self._killFlag.is_set()

    def stop(self, wait: bool = True) -> None:
        logging.getLogger("coretexpylib").info(">> [Coretex] Stopping the Task Run worker thread")
        self._stopFlag.set()

        if wait:
            self.join()

    def __enter__(self) -> Self:
        self.start()
        return self

    def __exit__(
        self,
        exceptionType: Optional[Type[BaseException]],
        exceptionValue: Optional[BaseException],
        exceptionTraceback: Optional[TracebackType]
    ) -> None:

        if self.is_alive():
            self.stop()

    def kill(self) -> None:
        logging.getLogger("coretexpylib").info(">> [Coretex] Killing the Task Run worker thread")

        self._killFlag.set()
        self.stop()

    def _update(self, sendMetrics: bool) -> None:
        logging.getLogger("coretexpylib").debug(">> [Coretex] Heartbeat")
        self.taskRun.updateStatus()  # updateStatus without params is considered heartbeat

        if sendMetrics:
            logging.getLogger("coretexpylib").debug(">> [Coretex] Uploading metrics")
            metrics.upload(self.taskRun)

    def run(self) -> None:
        try:
            metrics.create(self.taskRun)
            sendMetrics = True
        except NetworkRequestError:
            logging.getLogger("coretexpylib").info("Failed to initialize Task metrics")
            sendMetrics = False

        logging.getLogger("coretexpylib").info("TaskRun worker succcessfully started")

        # If local use current working dir, else use task path
        root = Path.cwd() if self.taskRun.isLocal else self.taskRun.taskPath

        # Start tracking files which are created inside current working directory
        with artifacts.track(root) as artifactsTracker:
            while not self.isStopped:
                # Measure elapsed time to calculate for how long should the process sleep
                duration, _ = measure(self._update, sendMetrics)

                # Make sure that metrics and heartbeat are sent every UPDATE_INTERVAL seconds
                if duration < UPDATE_INTERVAL:
                    sleepTime = UPDATE_INTERVAL - duration
                    logging.getLogger("coretexpylib").debug(f">> [Coretex] Task Run worker sleeping for {sleepTime}s")
                    time.sleep(sleepTime)

            # Only upload artifacts if worker was not killed
            if not self.isKilled:
                artifactsTracker.uploadTrackedArtifacts(self.taskRun, root)
            else:
                logging.getLogger("coretexpylib").warning(">> [Coretex] Task Run worker killed, skipping upload of automatically tracked Artifacts")
