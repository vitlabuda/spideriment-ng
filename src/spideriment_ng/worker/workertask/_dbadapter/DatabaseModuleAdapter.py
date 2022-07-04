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
import asyncio
import contextlib
from spideriment_ng.helpers.FlagCarrier import FlagCarrier
from spideriment_ng.helpers.containers.document.URLContainer import URLContainer
from spideriment_ng.modules.databases.DatabaseModuleIface import DatabaseModuleIface
from spideriment_ng.modules.databases.CrawledURLHandleIface import CrawledURLHandleIface
from spideriment_ng.modules.databases.exc.DatabaseModuleBaseExc import DatabaseModuleBaseExc
from spideriment_ng.worker.di import WORKER_DI_NS
from spideriment_ng.worker.workertask._dbadapter.CrawlHandleIface import CrawlHandleIface
from spideriment_ng.worker.workertask._dbadapter._CrawlHandle import _CrawlHandle


class DatabaseModuleAdapter:  # DP: Adapter
    _AVAILABLE_LINKS_FOR_CRAWLING_CHECK_INTERVAL: Final[float] = 1.0

    @WORKER_DI_NS.inject_dependencies("database")
    async def announce_start_urls(self, validated_absolute_start_urls: Sequence[URLContainer], database: DatabaseModuleIface) -> None:
        await database.announce_start_urls(validated_absolute_start_urls)

    @contextlib.asynccontextmanager  # 'None' means that the termination flag has been set to 'True' before a URL to crawl could be fetched from the database.
    async def next_url_to_crawl(self) -> Optional[CrawlHandleIface]:
        original_url_handle = await self._get_url_to_crawl_from_db_when_available()

        if original_url_handle is None:
            yield None
        else:
            crawl_handle = _CrawlHandle(original_url_handle)
            try:
                yield crawl_handle
            finally:
                await crawl_handle.finalize()

    @WORKER_DI_NS.inject_dependencies("database", "termination_flag_carrier")
    async def _get_url_to_crawl_from_db_when_available(self, database: DatabaseModuleIface, termination_flag_carrier: FlagCarrier) -> Optional[CrawledURLHandleIface]:
        original_url_handle = None
        while (original_url_handle is None) and (not termination_flag_carrier.get()):
            try:
                original_url_handle = await database.get_url_to_crawl()
            except DatabaseModuleBaseExc as e:
                if e.is_caused_by_no_more_links_to_crawl():
                    await asyncio.sleep(self.__class__._AVAILABLE_LINKS_FOR_CRAWLING_CHECK_INTERVAL)
                else:
                    raise e

        # 'None' means that the termination flag has been set to 'True' before a URL to crawl could be fetched from the database.
        return original_url_handle
