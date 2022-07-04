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
import abc
import os
import fcntl
from spideriment_ng.logger.LoggingStrategyIface import LoggingStrategyIface


class _TextIOLoggingStrategyBase(LoggingStrategyIface, metaclass=abc.ABCMeta):
    _NEWLINE: Final[str] = os.linesep

    def __init__(self, text_output_stream: TextIO):
        self._text_output_stream: Final[TextIO] = text_output_stream

    def _write_log_string_to_text_output_stream(self, log_string: str) -> None:
        try:
            # Multiple processes (supervisor + multiple workers + possibly other running programs) might be trying to write to the output stream concurrently
            fcntl.flock(self._text_output_stream.fileno(), fcntl.LOCK_EX)
            try:
                self._text_output_stream.write(log_string + self.__class__._NEWLINE)
                self._text_output_stream.flush()
            finally:
                fcntl.flock(self._text_output_stream.fileno(), fcntl.LOCK_UN)
        except OSError:
            # This exception is being ignored intentionally, as a logger failure is not a valid reason to crash the
            #  program (in the vast majority of cases)
            pass
