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


from typing import Final, Optional, Sequence, Tuple
from spideriment_ng.config.Configuration import Configuration
from spideriment_ng.logger.Logger import Logger
from spideriment_ng.logger.LogSeverity import LogSeverity
from spideriment_ng.helpers.CountCarrier import CountCarrier
from spideriment_ng.helpers.CrawlingErrorReason import CrawlingErrorReason
from spideriment_ng.helpers.containers.FetchedFileContainer import FetchedFileContainer
from spideriment_ng.helpers.containers.document.DocumentContainer import DocumentContainer
from spideriment_ng.helpers.containers.document.URLContainer import URLContainer
from spideriment_ng.modules.fetchers.FetcherModuleIface import FetcherModuleIface
from spideriment_ng.modules.fetchers.exc.FetcherModuleBaseExc import FetcherModuleBaseExc
from spideriment_ng.modules.fetchers.exc.FetcherModuleExcType import FetcherModuleExcType
from spideriment_ng.modules.databases.CrawledURLHandleIface import CrawledURLHandleIface
from spideriment_ng.modules.documentparsers.DocumentParserModuleIface import DocumentParserModuleIface
from spideriment_ng.modules.documentparsers.exc.DocumentParserModuleBaseExc import DocumentParserModuleBaseExc
from spideriment_ng.modules.documentparsers.exc.DocumentParserModuleExcType import DocumentParserModuleExcType
from spideriment_ng.worker.di import WORKER_DI_NS
from spideriment_ng.worker.workertask._dbadapter.DatabaseModuleAdapter import DatabaseModuleAdapter  # noqa
from spideriment_ng.worker.workertask._dbadapter.CrawlHandleIface import CrawlHandleIface  # noqa
from spideriment_ng.worker.workertask._robotassessor.RobotAssessor import RobotAssessor  # noqa
from spideriment_ng.worker.workertask._normalizers.DocumentNormalizer import DocumentNormalizer  # noqa
from spideriment_ng.worker.workertask._normalizers.URLNormalizer import URLNormalizer  # noqa
from spideriment_ng.worker.workertask._normalizers.exc.NormalizerBaseExc import NormalizerBaseExc  # noqa
from spideriment_ng.worker.workertask._crawler.exc.CrawlingErrorOccurredExc import CrawlingErrorOccurredExc
from spideriment_ng.worker.workertask._crawler.exc.CrawlingDelayOccurredExc import CrawlingDelayOccurredExc


class Crawler:
    def __init__(self, database_module_adapter: DatabaseModuleAdapter, robot_assessor: RobotAssessor,
                 url_normalizer: URLNormalizer, document_normalizer: DocumentNormalizer):
        self._database_module_adapter: Final[DatabaseModuleAdapter] = database_module_adapter
        self._robot_assessor: Final[RobotAssessor] = robot_assessor
        self._url_normalizer: Final[URLNormalizer] = url_normalizer
        self._document_normalizer: Final[DocumentNormalizer] = document_normalizer

    @WORKER_DI_NS.inject_dependencies("logger")
    async def crawl_one_document(self, logger: Logger) -> None:
        async with self._database_module_adapter.next_url_to_crawl() as crawl_handle:
            if crawl_handle is None:
                return

            crawled_url_string = crawl_handle.get_url_to_crawl().get_url_in_container().get_url()
            try:
                validated_crawled_document = await self._crawl_one_document_and_return_it(crawl_handle)

            except CrawlingDelayOccurredExc as delay_exc:
                await crawl_handle.delay(delay_exc.get_delayed_for())
                logger.log(LogSeverity.DEBUG, f"Crawling DELAY: {repr(crawled_url_string)} - {delay_exc.get_delayed_for()} seconds")

            except CrawlingErrorOccurredExc as error_exc:
                await crawl_handle.error(error_exc.get_error_reason())
                logger.log(LogSeverity.DEBUG, f"Crawling ERROR: {repr(crawled_url_string)} - {str(error_exc.get_error_reason())}")

            else:
                await crawl_handle.success(validated_crawled_document)
                logger.log(LogSeverity.DEBUG, f"Crawling SUCCESS: {repr(crawled_url_string)}")

    async def _crawl_one_document_and_return_it(self, crawl_handle: CrawlHandleIface) -> DocumentContainer:
        validated_absolute_final_url, fetched_file = await self._handle_possible_redirects_and_fetch_document(crawl_handle)

        unvalidated_document = await self._parse_fetched_document(fetched_file)
        del fetched_file  # Memory saving

        return self._validate_document_by_running_it_through_normalizer(
            validated_absolute_document_url=validated_absolute_final_url,
            unvalidated_document=unvalidated_document
        )

    @WORKER_DI_NS.inject_dependencies("fetcher", "configuration")
    async def _handle_possible_redirects_and_fetch_document(self, crawl_handle: CrawlHandleIface, fetcher: FetcherModuleIface, configuration: Configuration) -> Tuple[URLContainer, FetchedFileContainer]:
        limits_config = configuration.get_limits_configuration()

        redirect_count_carrier = CountCarrier(initial_value=0)
        raw_original_url_handle = crawl_handle.get_url_to_crawl()

        validated_absolute_original_url = self._normalize_document_url_from_db_in_crawled_url_handle(raw_original_url_handle)
        validated_absolute_current_url = validated_absolute_original_url

        while True:
            await self._check_robots_txt_for_url(validated_absolute_current_url, raw_original_url_handle.was_delayed())

            try:
                fetched_file = await fetcher.fetch(
                    validated_absolute_url=validated_absolute_current_url,
                    max_size=limits_config.get_max_document_size(),
                    timeout=limits_config.get_request_timeout()
                )
            except FetcherModuleBaseExc as e:
                exc_type = e.get_exception_type()
                if exc_type == FetcherModuleExcType.REDIRECT:
                    validated_absolute_current_url = self._handle_redirect_and_return_redirected_url(
                        redirect_count_carrier=redirect_count_carrier,
                        validated_absolute_current_url=validated_absolute_current_url,
                        unvalidated_nonabsolute_redirect_url=e.get_unvalidated_nonabsolute_redirect_url()
                    )
                elif exc_type == FetcherModuleExcType.UNEXPECTED_ERROR:
                    raise e
                else:
                    raise CrawlingErrorOccurredExc({
                        FetcherModuleExcType.CONNECTION_ERROR: CrawlingErrorReason.FETCH_CONNECTION_ERROR,
                        FetcherModuleExcType.NOT_FOUND: CrawlingErrorReason.FETCH_NOT_FOUND,
                        FetcherModuleExcType.FORBIDDEN: CrawlingErrorReason.FETCH_FORBIDDEN,
                        FetcherModuleExcType.SERVER_ERROR: CrawlingErrorReason.FETCH_SERVER_ERROR,
                        FetcherModuleExcType.UNCATEGORIZED_ERROR: CrawlingErrorReason.FETCH_UNCATEGORIZED_ERROR
                    }[exc_type])
            else:
                validated_absolute_final_url = await self._announce_final_url_if_necessary_and_return_it(
                    crawl_handle=crawl_handle,
                    validated_absolute_original_url=validated_absolute_original_url,
                    validated_absolute_final_url=validated_absolute_current_url
                )

                return validated_absolute_final_url, fetched_file

    @WORKER_DI_NS.inject_dependencies("configuration")
    async def _check_robots_txt_for_url(self, validated_absolute_url: URLContainer, was_delayed: bool, configuration: Configuration) -> None:
        robot_assessment = await self._robot_assessor.assess(validated_absolute_url)

        if not robot_assessment.is_url_crawlable():
            raise CrawlingErrorOccurredExc(CrawlingErrorReason.ROBOTS_FORBIDDEN)

        if not was_delayed:
            crawling_delay = robot_assessment.get_crawling_delay()
            if (crawling_delay < 0) or (crawling_delay > configuration.get_limits_configuration().get_max_crawling_delay()):
                raise CrawlingErrorOccurredExc(CrawlingErrorReason.ROBOTS_DELAY_TOO_LONG)
            if crawling_delay > 0:
                raise CrawlingDelayOccurredExc(crawling_delay)

    @WORKER_DI_NS.inject_dependencies("configuration")
    def _handle_redirect_and_return_redirected_url(self, redirect_count_carrier: CountCarrier, validated_absolute_current_url: URLContainer, unvalidated_nonabsolute_redirect_url: Optional[URLContainer], configuration: Configuration) -> URLContainer:
        assert (unvalidated_nonabsolute_redirect_url is not None)

        if redirect_count_carrier.get() >= configuration.get_limits_configuration().get_max_redirects():
            raise CrawlingErrorOccurredExc(CrawlingErrorReason.FETCH_TOO_MANY_REDIRECTS)
        redirect_count_carrier.increment()

        try:
            return self._url_normalizer.use_on_possibly_relative_url(
                validated_absolute_base_url=validated_absolute_current_url,
                unvalidated_nonabsolute_url=unvalidated_nonabsolute_redirect_url
            )
        except NormalizerBaseExc:
            raise CrawlingErrorOccurredExc(CrawlingErrorReason.VALIDATION_URL_PROBLEM)

    async def _announce_final_url_if_necessary_and_return_it(self, crawl_handle: CrawlHandleIface, validated_absolute_original_url: URLContainer, validated_absolute_final_url: URLContainer) -> URLContainer:
        # If the original and final URLs are the same (either due to a redirect not occurring or due to a "weird"
        #  redirect loop), nothing is reported back to the database
        if validated_absolute_original_url.get_url() == validated_absolute_final_url.get_url():
            return validated_absolute_original_url

        raw_final_url_handle = await crawl_handle.announce_redirect(validated_absolute_final_url)
        if raw_final_url_handle is None:
            raise CrawlingErrorOccurredExc(CrawlingErrorReason.FINAL_URL_NOT_CRAWLABLE)

        return self._normalize_document_url_from_db_in_crawled_url_handle(raw_final_url_handle)

    def _normalize_document_url_from_db_in_crawled_url_handle(self, crawled_url_handle: CrawledURLHandleIface) -> URLContainer:
        try:
            return self._url_normalizer.use_on_absolute_url(crawled_url_handle.get_url_in_container())
        except NormalizerBaseExc:
            raise CrawlingErrorOccurredExc(CrawlingErrorReason.VALIDATION_URL_PROBLEM)

    @WORKER_DI_NS.inject_dependencies("ordered_document_parsers")
    async def _parse_fetched_document(self, fetched_file: FetchedFileContainer, ordered_document_parsers: Sequence[DocumentParserModuleIface]) -> DocumentContainer:
        for document_parser in ordered_document_parsers:
            try:
                return await document_parser.parse(fetched_file)
            except DocumentParserModuleBaseExc as e:
                exc_type = e.get_exception_type()
                if exc_type == DocumentParserModuleExcType.UNEXPECTED_ERROR:
                    raise e
                if exc_type != DocumentParserModuleExcType.UNSUPPORTED_TYPE:
                    raise CrawlingErrorOccurredExc({
                        DocumentParserModuleExcType.CUT_OFF_CONTENT: CrawlingErrorReason.PARSE_CUT_OFF_CONTENT,
                        DocumentParserModuleExcType.INVALID_FORMAT: CrawlingErrorReason.PARSE_INVALID_FORMAT,
                        DocumentParserModuleExcType.INVALID_CONTENT: CrawlingErrorReason.PARSE_INVALID_CONTENT,
                        DocumentParserModuleExcType.FORBIDDEN: CrawlingErrorReason.PARSE_FORBIDDEN,
                        DocumentParserModuleExcType.UNCATEGORIZED_ERROR: CrawlingErrorReason.PARSE_UNCATEGORIZED_ERROR
                    }[exc_type])

        raise CrawlingErrorOccurredExc(CrawlingErrorReason.PARSE_UNSUPPORTED_TYPE)

    def _validate_document_by_running_it_through_normalizer(self, validated_absolute_document_url: URLContainer, unvalidated_document: DocumentContainer) -> DocumentContainer:
        try:
            return self._document_normalizer.use(
                validated_absolute_document_url=validated_absolute_document_url,
                unvalidated_document=unvalidated_document
            )
        except NormalizerBaseExc:
            raise CrawlingErrorOccurredExc(CrawlingErrorReason.VALIDATION_DOCUMENT_PROBLEM)
