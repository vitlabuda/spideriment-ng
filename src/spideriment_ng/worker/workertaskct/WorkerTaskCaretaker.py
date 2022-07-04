#!/bin/false

# Copyright (c) 2022 Vít Labuda. All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the
# following conditions are met:
#  1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following
#     disclaimer.
#  2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the
#     following disclaimer in the documentation and/or other materials provided with the distribution.
#  3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote
#     products derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
# INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


from typing import Sequence, Set
import asyncio
from spideriment_ng.config.Configuration import Configuration
from spideriment_ng.logger.Logger import Logger
from spideriment_ng.logger.LogSeverity import LogSeverity
from spideriment_ng.helpers.FlagCarrier import FlagCarrier
from spideriment_ng.worker.di import WORKER_DI_NS
from spideriment_ng.worker.workertaskct._WorkerTask import _WorkerTask
from spideriment_ng.worker.workertask.WorkerTaskMain import WorkerTaskMain
from spideriment_ng.worker.workertaskct.exc.WorkerTaskDiedExc import WorkerTaskDiedExc


class WorkerTaskCaretaker:
    @WORKER_DI_NS.inject_dependencies("logger")
    async def run(self, logger: Logger) -> None:
        tasks = self._start_worker_tasks()
        logger.log(LogSeverity.DEBUG, f"{len(tasks)} worker tasks started.")

        await self._monitor_worker_tasks(tasks)

        logger.log(LogSeverity.DEBUG, f"All {len(tasks)} worker tasks finished.")

    @WORKER_DI_NS.inject_dependencies("configuration", "logger")
    def _start_worker_tasks(self, configuration: Configuration, logger: Logger) -> Sequence[_WorkerTask]:
        tasks = []
        for task_id in range(1, configuration.get_limits_configuration().get_worker_tasks_per_process() + 1):
            logger.log(LogSeverity.DEBUG, f"Starting worker task with ID {task_id}...")

            new_task = asyncio.create_task(WorkerTaskMain().main(task_id))
            tasks.append(_WorkerTask(task_id, new_task))

        return tuple(tasks)

    @WORKER_DI_NS.inject_dependencies("logger")
    async def _monitor_worker_tasks(self, tasks: Sequence[_WorkerTask], logger: Logger) -> None:
        pending_tasks = set(task.get_worker_task() for task in tasks)

        while len(pending_tasks) > 0:
            finished_tasks, pending_tasks = await asyncio.wait(pending_tasks, return_when=asyncio.FIRST_COMPLETED)
            await self._check_finished_tasks(finished_tasks)

            logger.log(LogSeverity.DEBUG, f"{len(finished_tasks)} worker tasks finished, {len(pending_tasks)} worker tasks pending...")

    @WORKER_DI_NS.inject_dependencies("termination_flag_carrier")
    async def _check_finished_tasks(self, finished_tasks: Set[asyncio.Task], termination_flag_carrier: FlagCarrier) -> None:
        for finished_task in finished_tasks:
            # If the task terminates due to an exception, it is re-reaised there
            await finished_task

            # If the task does not terminate due to an exception, check if the program is supposed to terminate and if
            #  not, raise an exception
            if not termination_flag_carrier.get():
                raise WorkerTaskDiedExc()
