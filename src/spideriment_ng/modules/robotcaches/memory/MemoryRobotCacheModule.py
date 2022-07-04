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


from __future__ import annotations
from typing import Final, Dict
import time
import urllib.robotparser
from datalidator.blueprints.impl.ObjectBlueprint import ObjectBlueprint
from spideriment_ng.modules.ModuleInfo import ModuleInfo
from spideriment_ng.modules.ModuleType import ModuleType
from spideriment_ng.modules.robotcaches.RobotCacheModuleIface import RobotCacheModuleIface
from spideriment_ng.modules.robotcaches.memory._MemoryRobotCacheModuleConfigModel import _MemoryRobotCacheModuleConfigModel
from spideriment_ng.modules.robotcaches.memory._CacheEntry import _CacheEntry
from spideriment_ng.modules.robotcaches.memory.exc.MemoryCacheMissExc import MemoryCacheMissExc


class MemoryRobotCacheModule(RobotCacheModuleIface):
    _MODULE_INFO: Final[ModuleInfo] = ModuleInfo(
        type_=ModuleType.ROBOT_CACHE,
        name="memory",
        configuration_blueprint=ObjectBlueprint(_MemoryRobotCacheModuleConfigModel)
    )

    # Since clearing the cache is somewhat computationally intensive, entries are removed in "bursts" - up to the following fraction of the maximum cache size is removed at once, so the cache does not have to be cleared that often
    _CLEAR_CACHE_BURST_FRACTION: Final[float] = (1 / 10)
    _CLEAR_CACHE_MINIMUM_SECONDS_SINCE_LAST_HIT: Final[int] = 20

    @classmethod
    def get_module_info(cls) -> ModuleInfo:
        return cls._MODULE_INFO

    def __init__(self, max_entries: int):
        self._cache_dict: Final[Dict[str, _CacheEntry]] = dict()
        self._max_entries: Final[int] = max_entries
        self._clear_cache_burst: Final[int] = max(int(max_entries * self.__class__._CLEAR_CACHE_BURST_FRACTION), 1)
        self._operational: bool = True

    @classmethod
    async def create_instance(cls, module_options: _MemoryRobotCacheModuleConfigModel, instance_name: str) -> MemoryRobotCacheModule:
        return cls(module_options.max_entries)

    async def destroy_instance(self) -> None:
        assert self._operational
        self._operational = False

        self._cache_dict.clear()

    async def retrieve_from_cache(self, key: str) -> urllib.robotparser.RobotFileParser:
        assert self._operational

        try:
            cache_entry = self._cache_dict[key]
        except KeyError:
            raise MemoryCacheMissExc(key)

        cache_entry.set_last_hit_timestamp(self._get_current_timestamp())

        return cache_entry.get_robot_parser()

    async def put_into_cache(self, key: str, robot_parser: urllib.robotparser.RobotFileParser) -> None:
        assert self._operational

        self._clear_cache_if_necessary()

        if (key in self._cache_dict) or self._is_there_space_in_cache():
            self._cache_dict[key] = _CacheEntry(robot_parser, self._get_current_timestamp())

    def _is_there_space_in_cache(self) -> bool:
        return len(self._cache_dict) < self._max_entries

    def _get_current_timestamp(self) -> int:
        return int(time.time())

    def _clear_cache_if_necessary(self) -> None:
        if self._is_there_space_in_cache():
            return

        current_timestamp = self._get_current_timestamp()

        to_be_removed = []
        for key, cache_entry in self._cache_dict.items():
            seconds_since_last_hit = (current_timestamp - cache_entry.get_last_hit_timestamp())
            if seconds_since_last_hit >= self.__class__._CLEAR_CACHE_MINIMUM_SECONDS_SINCE_LAST_HIT:
                to_be_removed.append((key, seconds_since_last_hit))

        to_be_removed.sort(key=lambda item: item[1], reverse=True)  # The "oldest" entries will be first
        to_be_removed = to_be_removed[0:self._clear_cache_burst]

        for key, _ in to_be_removed:
            del self._cache_dict[key]
