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


from typing import Final, Any
from sidein.providers.DependencyProviderInterface import DependencyProviderInterface
from spideriment_ng.config.Configuration import Configuration
from spideriment_ng.logger.Logger import Logger
from spideriment_ng.supervisor.di.exc.InvalidSupervisorDependencyRequestedExc import InvalidSupervisorDependencyRequestedExc


class SupervisorDependencyProvider(DependencyProviderInterface):
    def __init__(self, configuration: Configuration, logger: Logger):
        self._configuration: Final[Configuration] = configuration
        self._logger: Final[Logger] = logger

    def get_configuration(self) -> Configuration:
        return self._configuration

    def get_logger(self) -> Logger:
        return self._logger

    def get_dependency(self, name: str) -> Any:
        try:
            # Dependency names are not saved in constants because they have to match function argument names.
            return ({
                "configuration": self._configuration,
                "logger": self._logger
            }[name])
        except KeyError:
            raise InvalidSupervisorDependencyRequestedExc(name)
