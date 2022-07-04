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
from spideriment_ng.config.GenericConfiguration import GenericConfiguration
from spideriment_ng.config.LimitsConfiguration import LimitsConfiguration
from spideriment_ng.config.FilteringConfiguration import FilteringConfiguration
from spideriment_ng.config.ConfiguredModule import ConfiguredModule
from spideriment_ng.modules.fetchers.FetcherModuleIface import FetcherModuleIface
from spideriment_ng.modules.databases.DatabaseModuleIface import DatabaseModuleIface
from spideriment_ng.modules.documentparsers.DocumentParserModuleIface import DocumentParserModuleIface
from spideriment_ng.modules.robotcaches.RobotCacheModuleIface import RobotCacheModuleIface


class Configuration:
    def __init__(self, generic_configuration: GenericConfiguration, limits_configuration: LimitsConfiguration,
                 filtering_configuration: FilteringConfiguration, fetcher_module: ConfiguredModule[FetcherModuleIface],
                 database_module: ConfiguredModule[DatabaseModuleIface], ordered_document_parser_modules: Sequence[ConfiguredModule[DocumentParserModuleIface]],
                 ordered_robot_cache_modules: Sequence[ConfiguredModule[RobotCacheModuleIface]]):

        self._generic_configuration: Final[GenericConfiguration] = generic_configuration
        self._limits_configuration: Final[LimitsConfiguration] = limits_configuration
        self._filtering_configuration: Final[FilteringConfiguration] = filtering_configuration
        self._fetcher_module: Final[ConfiguredModule[FetcherModuleIface]] = fetcher_module
        self._database_module: Final[ConfiguredModule[DatabaseModuleIface]] = database_module
        self._ordered_document_parser_modules: Final[Tuple[ConfiguredModule[DocumentParserModuleIface], ...]] = tuple(ordered_document_parser_modules)
        self._ordered_robot_cache_modules: Final[Tuple[ConfiguredModule[RobotCacheModuleIface], ...]] = tuple(ordered_robot_cache_modules)

    def get_generic_configuration(self) -> GenericConfiguration:
        return self._generic_configuration

    def get_limits_configuration(self) -> LimitsConfiguration:
        return self._limits_configuration

    def get_filtering_configuration(self) -> FilteringConfiguration:
        return self._filtering_configuration

    def get_fetcher_module(self) -> ConfiguredModule[FetcherModuleIface]:
        return self._fetcher_module

    def get_database_module(self) -> ConfiguredModule[DatabaseModuleIface]:
        return self._database_module

    def get_ordered_document_parser_modules(self) -> Sequence[ConfiguredModule[DocumentParserModuleIface]]:
        return self._ordered_document_parser_modules

    def get_ordered_robot_cache_modules(self) -> Sequence[ConfiguredModule[RobotCacheModuleIface]]:
        return self._ordered_robot_cache_modules
