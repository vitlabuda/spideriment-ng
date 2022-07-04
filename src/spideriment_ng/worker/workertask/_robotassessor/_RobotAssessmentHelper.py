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


from typing import Final, Tuple
import math
import urllib.robotparser
from spideriment_ng.worker.workertask._robotassessor.RobotAssessment import RobotAssessment


class _RobotAssessmentHelper:
    _ASSESSED_USER_AGENTS: Final[Tuple[str, ...]] = (
        "spideriment", "Spideriment", "SPIDERIMENT",
        "spideriment-ng", "Spideriment-NG", "SPIDERIMENT-NG",
        "spideriment_ng", "Spideriment_NG", "SPIDERIMENT_NG"
    )

    def generate_fallback_assessment(self) -> RobotAssessment:
        return RobotAssessment(
            url_crawlable=True,
            crawling_delay=0
        )

    def assess_parsed_robots_file(self, assessed_url: str, parsed_robots_file: urllib.robotparser.RobotFileParser) -> RobotAssessment:
        url_crawlable = self._decide_whether_url_is_crawlable(assessed_url, parsed_robots_file)
        crawling_delay = max(
            self._get_crawl_delay(parsed_robots_file),
            self._get_crawl_delay_from_request_rate(parsed_robots_file)
        )

        return RobotAssessment(
            url_crawlable=url_crawlable,
            crawling_delay=crawling_delay
        )

    def _decide_whether_url_is_crawlable(self, assessed_url: str, parsed_robots_file: urllib.robotparser.RobotFileParser) -> bool:
        for user_agent in self.__class__._ASSESSED_USER_AGENTS:
            if not parsed_robots_file.can_fetch(user_agent, assessed_url):
                return False

        return True

    def _get_crawl_delay(self, parsed_robots_file: urllib.robotparser.RobotFileParser) -> int:
        longest_crawl_delay = 0
        for user_agent in self.__class__._ASSESSED_USER_AGENTS:
            current_crawl_delay = parsed_robots_file.crawl_delay(user_agent)
            if (current_crawl_delay is not None) and (current_crawl_delay > longest_crawl_delay):
                longest_crawl_delay = current_crawl_delay

        return longest_crawl_delay

    def _get_crawl_delay_from_request_rate(self, parsed_robots_file: urllib.robotparser.RobotFileParser) -> int:
        longest_crawl_delay = 0
        for user_agent in self.__class__._ASSESSED_USER_AGENTS:
            request_rate = parsed_robots_file.request_rate(user_agent)
            if request_rate is None:
                continue

            try:
                current_crawl_delay = math.ceil(request_rate.seconds / request_rate.requests)
            except ZeroDivisionError:
                continue

            if current_crawl_delay > longest_crawl_delay:
                longest_crawl_delay = current_crawl_delay

        return longest_crawl_delay
