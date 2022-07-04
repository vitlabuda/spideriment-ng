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


from typing import Sequence, Optional
import abc
from spideriment_ng.helpers.containers.document.URLContainer import URLContainer
from spideriment_ng.helpers.containers.document.DocumentContainer import DocumentContainer
from spideriment_ng.helpers.CrawlingErrorReason import CrawlingErrorReason
from spideriment_ng.modules.ModuleIface import ModuleIface
from spideriment_ng.modules.databases.CrawledURLHandleIface import CrawledURLHandleIface


class DatabaseModuleIface(ModuleIface, metaclass=abc.ABCMeta):
    # Keep in mind that each worker process instantiates its own modules, but the instances are shared between its
    #  worker tasks and therefore all modules must be asyncio-safe!

    @abc.abstractmethod
    async def announce_start_urls(self, validated_absolute_start_urls: Sequence[URLContainer]) -> None:
        """
        :raises DatabaseModuleBaseExc
        """

        raise NotImplementedError(self.__class__.announce_start_urls.__qualname__)

    @abc.abstractmethod
    async def get_url_to_crawl(self) -> CrawledURLHandleIface:
        """
        :raises DatabaseModuleBaseExc
        """

        raise NotImplementedError(self.__class__.get_url_to_crawl.__qualname__)

    @abc.abstractmethod  # The redirected URL must be different from the original URL!
    async def announce_redirected_url(self, original_url: CrawledURLHandleIface, validated_absolute_redirected_url: URLContainer) -> CrawledURLHandleIface:
        """
        :raises DatabaseModuleBaseExc
        """

        raise NotImplementedError(self.__class__.announce_redirected_url.__qualname__)

    @abc.abstractmethod
    async def finish_crawling_with_delay(self, original_url: CrawledURLHandleIface, delay_seconds: int) -> None:
        """
        :raises DatabaseModuleBaseExc
        """

        raise NotImplementedError(self.__class__.finish_crawling_with_delay.__qualname__)

    @abc.abstractmethod
    async def finish_crawling_with_error(self, original_url: CrawledURLHandleIface, redirected_url: Optional[CrawledURLHandleIface], error_reason: CrawlingErrorReason) -> None:
        """
        :raises DatabaseModuleBaseExc
        """

        raise NotImplementedError(self.__class__.finish_crawling_with_error.__qualname__)

    @abc.abstractmethod
    async def finish_crawling_with_success(self, original_url: CrawledURLHandleIface, redirected_url: Optional[CrawledURLHandleIface], validated_document: DocumentContainer) -> None:
        """
        :raises DatabaseModuleBaseExc
        """

        raise NotImplementedError(self.__class__.finish_crawling_with_success.__qualname__)
