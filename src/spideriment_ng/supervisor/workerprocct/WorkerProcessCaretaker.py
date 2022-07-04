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


from typing import Sequence, Final
import time
import os
import gc
import signal
import multiprocessing
from spideriment_ng.SpiderimentConstants import SpiderimentConstants
from spideriment_ng.config.Configuration import Configuration
from spideriment_ng.logger.Logger import Logger
from spideriment_ng.logger.LogSeverity import LogSeverity
from spideriment_ng.supervisor.di import SUPERVISOR_DI_NS
from spideriment_ng.supervisor.workerprocct._WorkerProcess import _WorkerProcess
from spideriment_ng.worker.WorkerMain import WorkerMain


class WorkerProcessCaretaker:
    _WORKER_PROCESS_MONITOR_INTERVAL: Final[float] = 0.5

    class _ProgramShouldTerminateExc(Exception):
        pass

    @SUPERVISOR_DI_NS.inject_dependencies("logger")
    def run(self, logger: Logger) -> None:
        processes = self._start_worker_processes()
        logger.log(LogSeverity.INFO, f"{len(processes)} worker processes started.")

        self._monitor_worker_processes_until_supervisor_signaled(processes)
        self._send_termination_signal_to_worker_processes(processes)
        self._join_worker_processes(processes)

        logger.log(LogSeverity.DEBUG, f"All {len(processes)} worker processes joined successfully!")

    @SUPERVISOR_DI_NS.inject_dependencies("configuration", "logger")
    def _start_worker_processes(self, configuration: Configuration, logger: Logger) -> Sequence[_WorkerProcess]:
        mp_context = multiprocessing.get_context("fork")

        processes = []
        for worker_id in range(1, configuration.get_limits_configuration().get_worker_processes() + 1):
            logger.log(LogSeverity.DEBUG, f"Starting worker process with ID {worker_id}...")

            self._force_garbage_collection_if_desired()  # Worker processes should inherit as little memory as possible (--> memory saving)

            new_process_object = mp_context.Process(target=self.__class__._worker_process_target, args=(worker_id, configuration), daemon=False)
            new_process_object.start()

            processes.append(_WorkerProcess(worker_id, new_process_object))  # noqa

        return tuple(processes)

    @SUPERVISOR_DI_NS.inject_dependencies("logger")
    def _monitor_worker_processes_until_supervisor_signaled(self, processes: Sequence[_WorkerProcess], logger: Logger) -> None:
        self._set_signal_handlers_for_supervisor_process()

        try:
            self._monitor_worker_processes(processes)
        except self.__class__._ProgramShouldTerminateExc:
            logger.log(LogSeverity.WARNING, "A signal has been received - please wait for the program to terminate.")

    @SUPERVISOR_DI_NS.inject_dependencies("logger")
    def _monitor_worker_processes(self, processes: Sequence[_WorkerProcess], logger: Logger) -> None:
        while True:
            for process in processes:
                if not process.get_process_object().is_alive():
                    logger.log(LogSeverity.ERROR, f"Worker process with ID {process.get_worker_id()} has died - the program will terminate soon!")
                    return

            self._force_garbage_collection_if_desired()  # Memory saving
            time.sleep(self.__class__._WORKER_PROCESS_MONITOR_INTERVAL)

    def _set_signal_handlers_for_supervisor_process(self) -> None:
        signal.signal(SpiderimentConstants.WORKER_PROCESS_TERMINATION_SIGNAL, signal.SIG_IGN)  # This signal is caught only by worker processes

        def _supervisor_signal_handler(ignored1, ignored2):  # noqa
            for _sh_signum in SpiderimentConstants.PROGRAM_TERMINATION_SIGNALS:
                signal.signal(_sh_signum, signal.SIG_IGN)  # The signal has been caught and there is no need to catch it again
            raise self.__class__._ProgramShouldTerminateExc()

        for signum in SpiderimentConstants.PROGRAM_TERMINATION_SIGNALS:
            signal.signal(signum, _supervisor_signal_handler)

    @SUPERVISOR_DI_NS.inject_dependencies("logger")
    def _send_termination_signal_to_worker_processes(self, processes: Sequence[_WorkerProcess], logger: Logger) -> None:
        for process in processes:
            logger.log(LogSeverity.DEBUG, f"Sending a termination signal to worker process with ID {process.get_worker_id()}...")

            process_object = process.get_process_object()
            if process_object.is_alive():
                os.kill(process_object.pid, SpiderimentConstants.WORKER_PROCESS_TERMINATION_SIGNAL)

    @SUPERVISOR_DI_NS.inject_dependencies("logger")
    def _join_worker_processes(self, processes: Sequence[_WorkerProcess], logger: Logger) -> None:
        for process in processes:
            logger.log(LogSeverity.DEBUG, f"Joining worker process with ID {process.get_worker_id()}...")
            process.get_process_object().join()
            logger.log(LogSeverity.DEBUG, f"Worker process with ID {process.get_worker_id()} joined successfully!")

    @SUPERVISOR_DI_NS.inject_dependencies("configuration")
    def _force_garbage_collection_if_desired(self, configuration: Configuration) -> None:
        if configuration.get_generic_configuration().get_force_garbage_collection():
            gc.collect()

    # This method runs in a worker process, not in the supervisor process!
    @staticmethod
    def _worker_process_target(worker_process_id: int, configuration: Configuration) -> None:
        WorkerMain().main(worker_process_id, configuration)
