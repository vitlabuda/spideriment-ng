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


from typing import Final, TextIO
import threading
import queue
from spideriment_ng.logger.textio._TextIOLoggingStrategyBase import _TextIOLoggingStrategyBase


class ThreadedTextIOLoggingStrategy(_TextIOLoggingStrategyBase):
    _LOG_QUEUE_MAX_SIZE: Final[int] = 384
    _TERMINATE_LOGGING_THREAD_SIGNALIZING_VALUE = None

    def __init__(self, text_output_stream: TextIO):
        _TextIOLoggingStrategyBase.__init__(self, text_output_stream)

        self._log_queue: Final[queue.Queue] = queue.Queue(maxsize=self.__class__._LOG_QUEUE_MAX_SIZE)
        self._logging_thread: Final[threading.Thread] = threading.Thread(target=self._logging_thread_target, daemon=True)
        self._logging_thread.start()  # The logger thread uses self._log_queue and self._text_output_stream, so it must not be started before these instance variables have been initialized!

    def process_log_string(self, log_string: str) -> None:
        assert self._logging_thread.is_alive()

        try:
            self._log_queue.put_nowait(log_string)
        except queue.Full:
            # This exception is being ignored intentionally, as a logger failure is not a valid reason to crash the
            #  program (in the vast majority of cases)
            pass

    def terminate(self) -> None:
        assert self._logging_thread.is_alive()

        self._log_queue.put(self.__class__._TERMINATE_LOGGING_THREAD_SIGNALIZING_VALUE)
        self._logging_thread.join()

    # This method runs in the logger thread, not in the "main" thread!
    def _logging_thread_target(self) -> None:
        while True:
            item = self._log_queue.get()
            if item == self.__class__._TERMINATE_LOGGING_THREAD_SIGNALIZING_VALUE:
                break

            self._write_log_string_to_text_output_stream(item)
