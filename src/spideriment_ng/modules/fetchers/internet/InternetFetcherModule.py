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
from typing import Final, Callable, Awaitable, Dict
import re
import urllib.parse
import aiohttp
import aiohttp_socks
from datalidator.blueprints.impl.ObjectBlueprint import ObjectBlueprint
from spideriment_ng.SpiderimentConstants import SpiderimentConstants
from spideriment_ng.modules.ModuleInfo import ModuleInfo
from spideriment_ng.modules.ModuleType import ModuleType
from spideriment_ng.exc.ThisShouldNeverHappenError import ThisShouldNeverHappenError
from spideriment_ng.helpers.containers.FetchedFileContainer import FetchedFileContainer
from spideriment_ng.helpers.containers.document.URLContainer import URLContainer
from spideriment_ng.modules.fetchers.FetcherModuleIface import FetcherModuleIface
from spideriment_ng.modules.fetchers.exc.FetcherModuleBaseExc import FetcherModuleBaseExc
from spideriment_ng.modules.fetchers.internet._InternetFetcherModuleConfigModel import _InternetFetcherModuleConfigModel
from spideriment_ng.modules.fetchers.internet.exc.InvalidProxyTypeExc import InvalidProxyTypeExc
from spideriment_ng.modules.fetchers.internet.exc.RedirectedExc import RedirectedExc
from spideriment_ng.modules.fetchers.internet.exc.ServerErrorOccurredExc import ServerErrorOccurredExc
from spideriment_ng.modules.fetchers.internet.exc.ConnectionErrorOccurredExc import ConnectionErrorOccurredExc


class InternetFetcherModule(FetcherModuleIface):
    _MODULE_INFO: Final[ModuleInfo] = ModuleInfo(
        type_=ModuleType.FETCHER,
        name="internet",
        configuration_blueprint=ObjectBlueprint(_InternetFetcherModuleConfigModel)
    )

    _DOWNLOAD_CHUNK_SIZE: Final[int] = 16384

    @classmethod
    def get_module_info(cls) -> ModuleInfo:
        return cls._MODULE_INFO

    def __init__(self, user_agent: str, proxy_url: str):
        self._user_agent: Final[str] = user_agent
        self._proxy_url: Final[str] = proxy_url
        self._parsed_proxy_url: Final[urllib.parse.SplitResult] = urllib.parse.urlsplit(proxy_url)
        self._fetcher_function: Final[Callable[[str, int, aiohttp.ClientTimeout], Awaitable[FetchedFileContainer]]] = self._get_fetcher_function_by_proxy_url(self._parsed_proxy_url)
        self._operational: bool = True

    def _get_fetcher_function_by_proxy_url(self, parsed_proxy_url: urllib.parse.SplitResult) -> Callable[[str, int, aiohttp.ClientTimeout], Awaitable[FetchedFileContainer]]:
        if parsed_proxy_url.scheme == "none":
            return self._fetch_without_proxy

        if re.match(r'^https?\Z', parsed_proxy_url.scheme):
            return self._fetch_using_http_proxy

        if re.match(r'^socks[45]h?\Z', parsed_proxy_url.scheme):
            return self._fetch_using_socks_proxy

        raise InvalidProxyTypeExc(parsed_proxy_url.scheme)

    @classmethod
    async def create_instance(cls, module_options: _InternetFetcherModuleConfigModel, instance_name: str) -> InternetFetcherModule:
        return cls(module_options.user_agent, module_options.proxy)

    async def destroy_instance(self) -> None:
        assert self._operational
        self._operational = False

    async def fetch(self, validated_absolute_url: URLContainer, max_size: int, timeout: int) -> FetchedFileContainer:
        assert self._operational
        assert (validated_absolute_url.is_validated() and validated_absolute_url.is_certainly_absolute())
        assert (max_size > 0)
        assert (timeout > 0)

        url = validated_absolute_url.get_url()
        try:
            timeout_object = aiohttp.ClientTimeout(total=timeout)
            return await self._fetcher_function(url, max_size, timeout_object)
        except (FetcherModuleBaseExc, AssertionError) as e:
            raise e
        except Exception:  # It is not clear what exceptions does 'aiohttp_socks' raise
            raise ConnectionErrorOccurredExc()

    async def _fetch_without_proxy(self, url: str, max_size: int, timeout_object: aiohttp.ClientTimeout) -> FetchedFileContainer:
        async with aiohttp.ClientSession(timeout=timeout_object, headers=self._generate_request_headers(), raise_for_status=False, auto_decompress=True, trust_env=False) as session:
            async with session.get(url, allow_redirects=False) as response:
                return await self._process_response(response, max_size)

    async def _fetch_using_http_proxy(self, url: str, max_size: int, timeout_object: aiohttp.ClientTimeout) -> FetchedFileContainer:
        async with aiohttp.ClientSession(timeout=timeout_object, headers=self._generate_request_headers(), raise_for_status=False, auto_decompress=True, trust_env=False) as session:
            async with session.get(url, proxy=self._proxy_url, allow_redirects=False) as response:
                return await self._process_response(response, max_size)

    async def _fetch_using_socks_proxy(self, url: str, max_size: int, timeout_object: aiohttp.ClientTimeout) -> FetchedFileContainer:
        async with aiohttp.ClientSession(connector=self._generate_new_socks_proxy_connector_from_proxy_url(), timeout=timeout_object, headers=self._generate_request_headers(), raise_for_status=False, auto_decompress=True, trust_env=False) as session:
            async with session.get(url, allow_redirects=False) as response:
                return await self._process_response(response, max_size)

    def _generate_new_socks_proxy_connector_from_proxy_url(self) -> aiohttp_socks.ProxyConnector:
        # As of now, 'aiohttp_socks.ProxyConnector.from_url' does not work with 'socks[45]h' URLs, so a custom URL
        #  parsing function is necessary.

        if self._parsed_proxy_url.scheme == "socks4":
            proxy_type = aiohttp_socks.ProxyType.SOCKS4
            rdns = False
        elif self._parsed_proxy_url.scheme == "socks4h":
            proxy_type = aiohttp_socks.ProxyType.SOCKS4
            rdns = True
        elif self._parsed_proxy_url.scheme == "socks5":
            proxy_type = aiohttp_socks.ProxyType.SOCKS5
            rdns = False
        elif self._parsed_proxy_url.scheme == "socks5h":
            proxy_type = aiohttp_socks.ProxyType.SOCKS5
            rdns = True
        else:
            raise ThisShouldNeverHappenError(f"An invalid proxy scheme ({repr(self._parsed_proxy_url.scheme)}) was encountered, even though it had been checked before!")

        return aiohttp_socks.ProxyConnector(
            proxy_type=proxy_type,
            host=self._parsed_proxy_url.hostname,  # None if not present
            port=self._parsed_proxy_url.port,  # None if not present
            username=self._parsed_proxy_url.username,  # None if not present
            password=self._parsed_proxy_url.password,  # None if not present
            rdns=rdns
        )

    async def _process_response(self, response: aiohttp.ClientResponse, max_size: int) -> FetchedFileContainer:
        # Handle redirects
        if "Location" in response.headers:
            redirect_url = response.headers["Location"].strip()
            raise RedirectedExc(unvalidated_nonabsolute_redirect_url=URLContainer(
                validated=False,
                certainly_absolute=False,
                url=redirect_url
            ))

        # Handle non-200 HTTP status codes
        if response.status != 200:
            raise ServerErrorOccurredExc(response.status)

        # Handle successful responses
        mime_type = response.content_type.strip()
        encoding = response.charset
        if encoding is not None:
            encoding = encoding.strip()

        recv_buffer = bytearray()
        cut_off = False
        async for chunk in response.content.iter_chunked(self.__class__._DOWNLOAD_CHUNK_SIZE):
            recv_buffer += chunk
            if len(recv_buffer) > max_size:
                cut_off = True
                break

        return FetchedFileContainer(
            data=bytes(recv_buffer[0:max_size]),
            are_data_cut_off=cut_off,
            hinted_mime_type=mime_type,
            hinted_encoding=encoding
        )

    def _generate_request_headers(self) -> Dict[str, str]:
        return {
            "User-Agent": self._user_agent.format(program_version=SpiderimentConstants.PROGRAM_VERSION)
        }
