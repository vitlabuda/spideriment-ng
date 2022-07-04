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


from typing import Final, Optional
from spideriment_ng.helpers.CrawlingErrorReason import CrawlingErrorReason
from spideriment_ng.helpers.containers.document.URLContainer import URLContainer
from spideriment_ng.helpers.containers.document.DocumentContainer import DocumentContainer
from spideriment_ng.modules.databases.CrawledURLHandleIface import CrawledURLHandleIface
from spideriment_ng.modules.databases.DatabaseModuleIface import DatabaseModuleIface
from spideriment_ng.modules.databases.exc.DatabaseModuleBaseExc import DatabaseModuleBaseExc
from spideriment_ng.worker.di import WORKER_DI_NS
from spideriment_ng.worker.workertask._dbadapter.CrawlHandleIface import CrawlHandleIface


class _CrawlHandle(CrawlHandleIface):
    _FALLBACK_ERROR_REASON: Final[CrawlingErrorReason] = CrawlingErrorReason.UNKNOWN_ERROR

    def __init__(self, original_url_handle: CrawledURLHandleIface):
        self._original_url_handle: Final[CrawledURLHandleIface] = original_url_handle
        self._redirected_url_handle: Optional[CrawledURLHandleIface] = None
        self._open: bool = True  # = True if no delay, error or success has been SUCCESSFULLY reported; False otherwise
        self._redirect_not_accepted: bool = False

    def get_url_to_crawl(self) -> CrawledURLHandleIface:
        return self._original_url_handle

    @WORKER_DI_NS.inject_dependencies("database")
    async def announce_redirect(self, validated_absolute_redirected_url: URLContainer, database: DatabaseModuleIface) -> Optional[CrawledURLHandleIface]:
        assert self._open
        assert (self._redirected_url_handle is None)  # A redirect may be announced only once
        assert (not self._redirect_not_accepted)

        try:
            self._redirected_url_handle = await database.announce_redirected_url(self._original_url_handle, validated_absolute_redirected_url)
        except DatabaseModuleBaseExc as e:
            if e.is_caused_by_unacceptable_redirected_url():
                self._redirect_not_accepted = True
                return None
            raise e

        return self._redirected_url_handle

    @WORKER_DI_NS.inject_dependencies("database")
    async def delay(self, delay_seconds: int, database: DatabaseModuleIface) -> None:
        assert self._open
        assert (self._redirected_url_handle is None)  # Delay detection is always performed before final URL detection is
        assert (not self._redirect_not_accepted)

        await database.finish_crawling_with_delay(self._original_url_handle, delay_seconds)

        self._open = False

    @WORKER_DI_NS.inject_dependencies("database")
    async def error(self, error_reason: CrawlingErrorReason, database: DatabaseModuleIface) -> None:
        assert self._open
        if self._redirect_not_accepted:
            assert (error_reason in (CrawlingErrorReason.FINAL_URL_NOT_CRAWLABLE, self.__class__._FALLBACK_ERROR_REASON))

        await database.finish_crawling_with_error(self._original_url_handle, self._redirected_url_handle, error_reason)

        self._open = False

    @WORKER_DI_NS.inject_dependencies("database")
    async def success(self, validated_document: DocumentContainer, database: DatabaseModuleIface) -> None:
        assert self._open
        assert (not self._redirect_not_accepted)

        await database.finish_crawling_with_success(self._original_url_handle, self._redirected_url_handle, validated_document)

        self._open = False

    async def finalize(self) -> None:
        if self._open:
            await self.error(self.__class__._FALLBACK_ERROR_REASON)
