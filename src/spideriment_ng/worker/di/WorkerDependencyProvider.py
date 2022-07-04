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


from typing import Final, Any, Sequence, Tuple
from sidein.providers.DependencyProviderInterface import DependencyProviderInterface
from spideriment_ng.config.Configuration import Configuration
from spideriment_ng.logger.Logger import Logger
from spideriment_ng.modules.fetchers.FetcherModuleIface import FetcherModuleIface
from spideriment_ng.modules.databases.DatabaseModuleIface import DatabaseModuleIface
from spideriment_ng.modules.documentparsers.DocumentParserModuleIface import DocumentParserModuleIface
from spideriment_ng.modules.robotcaches.RobotCacheModuleIface import RobotCacheModuleIface
from spideriment_ng.helpers.FlagCarrier import FlagCarrier
from spideriment_ng.worker.di.exc.InvalidWorkerDependencyRequestedExc import InvalidWorkerDependencyRequestedExc


class WorkerDependencyProvider(DependencyProviderInterface):
    def __init__(self, worker_process_id: int, configuration: Configuration, termination_flag_carrier: FlagCarrier, logger: Logger,
                 fetcher: FetcherModuleIface, database: DatabaseModuleIface, ordered_document_parsers: Sequence[DocumentParserModuleIface],
                 ordered_robot_caches: Sequence[RobotCacheModuleIface]):
        self._worker_process_id: Final[int] = worker_process_id
        self._configuration: Final[Configuration] = configuration
        self._termination_flag_carrier: Final[FlagCarrier] = termination_flag_carrier
        self._logger: Final[Logger] = logger
        self._fetcher: Final[FetcherModuleIface] = fetcher
        self._database: Final[DatabaseModuleIface] = database
        self._ordered_document_parsers: Final[Tuple[DocumentParserModuleIface, ...]] = tuple(ordered_document_parsers)
        self._ordered_robot_caches: Final[Tuple[RobotCacheModuleIface, ...]] = tuple(ordered_robot_caches)

    def get_worker_process_id(self) -> int:
        return self._worker_process_id

    def get_configuration(self) -> Configuration:
        return self._configuration

    def get_termination_flag_carrier(self) -> FlagCarrier:
        return self._termination_flag_carrier

    def get_logger(self) -> Logger:
        return self._logger

    def get_fetcher(self) -> FetcherModuleIface:
        return self._fetcher

    def get_database(self) -> DatabaseModuleIface:
        return self._database

    def get_ordered_document_parsers(self) -> Sequence[DocumentParserModuleIface]:
        return self._ordered_document_parsers

    def get_ordered_robot_caches(self) -> Sequence[RobotCacheModuleIface]:
        return self._ordered_robot_caches

    def get_dependency(self, name: str) -> Any:
        try:
            # Dependency names are not saved in constants because they have to match function argument names.
            return ({
                "worker_process_id": self._worker_process_id,
                "configuration": self._configuration,
                "termination_flag_carrier": self._termination_flag_carrier,
                "logger": self._logger,
                "fetcher": self._fetcher,
                "database": self._database,
                "ordered_document_parsers": self._ordered_document_parsers,
                "ordered_robot_caches": self._ordered_robot_caches
            }[name])
        except KeyError:
            raise InvalidWorkerDependencyRequestedExc(name)
