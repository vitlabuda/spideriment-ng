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


from typing import Final, Sequence, Tuple
import datetime
from spideriment_ng.logger.LogSeverity import LogSeverity
from spideriment_ng.logger.LoggingStrategyIface import LoggingStrategyIface


class Logger:
    _LOG_DATETIME_FORMAT: Final[str] = "%Y-%m-%d %H:%M:%S"

    def __init__(self, logging_strategy: LoggingStrategyIface, logged_severities: Sequence[LogSeverity], source_identifier: str):
        self._logging_strategy: Final[LoggingStrategyIface] = logging_strategy
        self._logged_severities: Final[Tuple[LogSeverity, ...]] = tuple(logged_severities)
        self._source_identifier: Final[str] = source_identifier
        self._operational: bool = True

    def log(self, severity: LogSeverity, message: str) -> None:
        assert self._operational

        if severity not in self._logged_severities:
            return

        log_string = "[{datetime} / {source} / {severity}] {message}".format(
            datetime=datetime.datetime.now().strftime(self.__class__._LOG_DATETIME_FORMAT),
            source=self._source_identifier,
            severity=self._get_string_representation_of_log_severity(severity),
            message=message
        )

        self._logging_strategy.process_log_string(log_string)

    def _get_string_representation_of_log_severity(self, severity: LogSeverity) -> str:
        severity_string = ({
            LogSeverity.ERROR: "ERROR",
            LogSeverity.WARNING: "WARN",
            LogSeverity.INFO: "INFO",
            LogSeverity.DEBUG: "DEBUG"
        }.get(severity, None))

        assert (severity_string is not None)

        return severity_string

    def terminate(self) -> None:
        assert self._operational
        self._operational = False

        self._logging_strategy.terminate()
