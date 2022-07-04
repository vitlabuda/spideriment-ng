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


from typing import Final, Optional, Sequence
import urllib.parse
import urllib.robotparser
from spideriment_ng.helpers.containers.document.URLContainer import URLContainer
from spideriment_ng.modules.robotcaches.RobotCacheModuleIface import RobotCacheModuleIface
from spideriment_ng.modules.robotcaches.exc.RobotCacheModuleBaseExc import RobotCacheModuleBaseExc
from spideriment_ng.worker.di import WORKER_DI_NS
from spideriment_ng.worker.workertask._robotassessor._RobotFetchHelper import _RobotFetchHelper
from spideriment_ng.worker.workertask._robotassessor._RobotAssessmentHelper import _RobotAssessmentHelper
from spideriment_ng.worker.workertask._robotassessor.RobotAssessment import RobotAssessment


class RobotAssessor:
    _ROBOTS_TXT_PATH: Final[str] = "/robots.txt"

    def __init__(self):
        self._robot_fetch_helper: Final[_RobotFetchHelper] = _RobotFetchHelper()
        self._robot_assessment_helper: Final[_RobotAssessmentHelper] = _RobotAssessmentHelper()

    async def assess(self, validated_absolute_assessed_url: URLContainer) -> RobotAssessment:
        assert (validated_absolute_assessed_url.is_validated() and validated_absolute_assessed_url.is_certainly_absolute())

        assessed_url = validated_absolute_assessed_url.get_url()

        robots_txt_url = self._get_robots_txt_url_from_input_url(assessed_url)
        parsed_robots_file = await self._get_parsed_robots_file(robots_txt_url)

        return self._assess_parsed_robots_file(assessed_url, parsed_robots_file)

    def _get_robots_txt_url_from_input_url(self, input_url: str) -> str:
        split_input_url = urllib.parse.urlsplit(input_url, allow_fragments=True)

        return urllib.parse.urlunsplit(urllib.parse.SplitResult(
            scheme=split_input_url.scheme,
            netloc=split_input_url.netloc,
            path=self.__class__._ROBOTS_TXT_PATH,
            query="",
            fragment=""
        ))  # noqa

    async def _get_parsed_robots_file(self, robots_txt_url: str) -> Optional[urllib.robotparser.RobotFileParser]:
        # Try caches first...
        parsed_robots_file = await self._get_parsed_robots_file_from_caches(robots_txt_url)
        if parsed_robots_file is not None:
            return parsed_robots_file

        # ... if no cache holds the file, try to fetch it
        parsed_robots_file = await self._get_parsed_robots_file_using_fetcher(robots_txt_url)
        if parsed_robots_file is None:
            return None

        # If the file is successfully fetched, cache it and return it
        await self._cache_fetched_robots_file(robots_txt_url, parsed_robots_file)
        return parsed_robots_file

    @WORKER_DI_NS.inject_dependencies("ordered_robot_caches")
    async def _get_parsed_robots_file_from_caches(self, robots_txt_url: str, ordered_robot_caches: Sequence[RobotCacheModuleIface]) -> Optional[urllib.robotparser.RobotFileParser]:
        for robot_cache in ordered_robot_caches:
            try:
                return await robot_cache.retrieve_from_cache(robots_txt_url)
            except RobotCacheModuleBaseExc as e:
                if not e.is_caused_by_cache_miss():
                    raise e

        return None

    async def _get_parsed_robots_file_using_fetcher(self, robots_txt_url: str) -> Optional[urllib.robotparser.RobotFileParser]:
        # The robots.txt URL was generated from a validated & absolute input (assessed) URL, so it can be considered
        #  validated & absolute too.
        validated_absolute_robots_txt_url = URLContainer(
            validated=True,
            certainly_absolute=True,
            url=robots_txt_url
        )

        return await self._robot_fetch_helper.fetch_robots_file(validated_absolute_robots_txt_url)

    @WORKER_DI_NS.inject_dependencies("ordered_robot_caches")
    async def _cache_fetched_robots_file(self, robots_txt_url: str, fetched_robots_file: urllib.robotparser.RobotFileParser, ordered_robot_caches: Sequence[RobotCacheModuleIface]) -> None:
        for robot_cache in ordered_robot_caches:  # The robots file is put into all the caches
            # Exceptions are not caught, since only "fatal" exceptions can occur when putting a new item into the caches
            await robot_cache.put_into_cache(robots_txt_url, fetched_robots_file)

    def _assess_parsed_robots_file(self, assessed_url: str, parsed_robots_file: Optional[urllib.robotparser.RobotFileParser]) -> RobotAssessment:
        if parsed_robots_file is None:
            return self._robot_assessment_helper.generate_fallback_assessment()

        return self._robot_assessment_helper.assess_parsed_robots_file(assessed_url, parsed_robots_file)
