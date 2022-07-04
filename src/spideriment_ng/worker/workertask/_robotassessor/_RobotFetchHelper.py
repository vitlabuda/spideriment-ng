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


from typing import Final, Optional, Tuple
import urllib.robotparser
from spideriment_ng.config.Configuration import Configuration
from spideriment_ng.helpers.containers.FetchedFileContainer import FetchedFileContainer
from spideriment_ng.helpers.containers.document.URLContainer import URLContainer
from spideriment_ng.helpers.decoding.DecodingHelper import DecodingHelper
from spideriment_ng.helpers.decoding.exc.DecodingHelperBaseExc import DecodingHelperBaseExc
from spideriment_ng.modules.fetchers.FetcherModuleIface import FetcherModuleIface
from spideriment_ng.modules.fetchers.exc.FetcherModuleBaseExc import FetcherModuleBaseExc
from spideriment_ng.worker.di import WORKER_DI_NS


class _RobotFetchHelper:
    _ALLOWED_MIME_TYPES: Final[Tuple[str, ...]] = ("text/plain",)
    _FALLBACK_ENCODING: Final[str] = "utf-8"

    def __init__(self):
        self._decoding_helper: Final[DecodingHelper] = DecodingHelper()

    # None means that the robots.txt file could not be downloaded or parsed (for whatever reason).
    async def fetch_robots_file(self, validated_absolute_robots_txt_url: URLContainer) -> Optional[urllib.robotparser.RobotFileParser]:
        downloaded_robots_txt = await self._download_robots_file_using_fetcher(validated_absolute_robots_txt_url)
        if downloaded_robots_txt is None:
            return None

        if not self._is_mime_type_allowed_for_robots_txt(downloaded_robots_txt.get_hinted_mime_type()):
            return None

        decoded_robots_txt_string = self._decode_binary_robots_txt_data(downloaded_robots_txt.get_data(), downloaded_robots_txt.get_hinted_encoding())
        if decoded_robots_txt_string is None:
            return None

        return self._parse_robots_txt_string(decoded_robots_txt_string)

    @WORKER_DI_NS.inject_dependencies("configuration", "fetcher")
    async def _download_robots_file_using_fetcher(self, validated_absolute_robots_txt_url: URLContainer, configuration: Configuration, fetcher: FetcherModuleIface) -> Optional[FetchedFileContainer]:
        limits_config = configuration.get_limits_configuration()

        try:
            return await fetcher.fetch(
                validated_absolute_url=validated_absolute_robots_txt_url,
                max_size=limits_config.get_max_robots_txt_size(),
                timeout=limits_config.get_request_timeout()
            )
        except FetcherModuleBaseExc:
            return None

    def _is_mime_type_allowed_for_robots_txt(self, mime_type: str) -> bool:
        return mime_type.strip().lower() in self.__class__._ALLOWED_MIME_TYPES

    def _decode_binary_robots_txt_data(self, binary_robots: bytes, hinted_encoding: Optional[str]) -> Optional[str]:
        # HTTP header
        if hinted_encoding is not None:
            try:
                return self._decoding_helper.validate_encoding_and_try_decoding_data_using_it(binary_robots, hinted_encoding)
            except DecodingHelperBaseExc:
                pass

        # Automatic detection
        try:
            return self._decoding_helper.try_detecting_encoding_and_try_decoding_data_using_it(binary_robots)
        except DecodingHelperBaseExc:
            pass

        # Fallback
        try:
            return self._decoding_helper.try_decoding_data_using_encoding(binary_robots, self.__class__._FALLBACK_ENCODING, ignore_errors=False)
        except DecodingHelperBaseExc:
            return None

    def _parse_robots_txt_string(self, decoded_robots_txt_string: str) -> Optional[urllib.robotparser.RobotFileParser]:
        lines = decoded_robots_txt_string.splitlines()

        robot_parser = urllib.robotparser.RobotFileParser()
        try:
            robot_parser.parse(lines)
        except Exception:  # noqa; It is not clear what exceptions does 'RobotFileParser' raise
            return None

        return robot_parser
