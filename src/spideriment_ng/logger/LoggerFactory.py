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


from typing import Final, Sequence, TextIO
import sys
import contextlib
from spideriment_ng.logger.Logger import Logger
from spideriment_ng.logger.LogSeverity import LogSeverity
from spideriment_ng.logger.textio.BlockingTextIOLoggingStrategy import BlockingTextIOLoggingStrategy
from spideriment_ng.logger.textio.ThreadedTextIOLoggingStrategy import ThreadedTextIOLoggingStrategy


class LoggerFactory:  # DP: Factory
    _LOGGER_TEXT_OUTPUT_STREAM: Final[TextIO] = sys.stdout

    _SUPERVISOR_PROCESS_SOURCE_IDENTIFIER: Final[str] = "C"
    _WORKER_PROCESS_SOURCE_IDENTIFIER_PATTERN: Final[str] = "W{worker_process_id}"

    @contextlib.contextmanager
    def acquire_logger_instance_for_supervisor_process(self, log_debug_messages: bool) -> Logger:
        # The blocking strategy is used, since the supervisor process does not do anything most of the time, so it does not matter that the logger can block the caller
        logger_instance = Logger(
            logging_strategy=BlockingTextIOLoggingStrategy(self.__class__._LOGGER_TEXT_OUTPUT_STREAM),
            logged_severities=self._generate_list_of_logged_severities_for_logger(log_debug_messages),
            source_identifier=self.__class__._SUPERVISOR_PROCESS_SOURCE_IDENTIFIER
        )

        try:
            yield logger_instance
        finally:
            logger_instance.terminate()

    @contextlib.contextmanager
    def acquire_logger_instance_for_worker_process(self, log_debug_messages: bool, worker_process_id: int) -> Logger:
        # The threaded strategy is used, since worker processes have more important things to do than waiting for a
        #  blocking logger until it writes out a message...
        # Even 'stdout' can be slow, for example when it is hooked to an SSH session which is connected over a
        #  high-latency or very low-speed Internet link...
        logger_instance = Logger(
            logging_strategy=ThreadedTextIOLoggingStrategy(self.__class__._LOGGER_TEXT_OUTPUT_STREAM),
            logged_severities=self._generate_list_of_logged_severities_for_logger(log_debug_messages),
            source_identifier=self.__class__._WORKER_PROCESS_SOURCE_IDENTIFIER_PATTERN.format(worker_process_id=worker_process_id)
        )

        try:
            yield logger_instance
        finally:
            logger_instance.terminate()

    def _generate_list_of_logged_severities_for_logger(self, log_debug_messages: bool) -> Sequence[LogSeverity]:
        list_of_severities = [LogSeverity.ERROR, LogSeverity.WARNING, LogSeverity.INFO]
        if log_debug_messages:
            list_of_severities.append(LogSeverity.DEBUG)

        return list_of_severities
