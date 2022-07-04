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


from typing import Final, Sequence
import gc
import urllib.parse
from spideriment_ng.config.Configuration import Configuration
from spideriment_ng.logger.Logger import Logger
from spideriment_ng.logger.LogSeverity import LogSeverity
from spideriment_ng.helpers.FlagCarrier import FlagCarrier
from spideriment_ng.helpers.containers.document.URLContainer import URLContainer
from spideriment_ng.worker.di import WORKER_DI_NS
from spideriment_ng.worker.workertask.exc.NoStartURLsExc import NoStartURLsExc
from spideriment_ng.worker.workertask.exc.InvalidStartURLExc import InvalidStartURLExc
from spideriment_ng.worker.workertask._dbadapter.DatabaseModuleAdapter import DatabaseModuleAdapter  # noqa
from spideriment_ng.worker.workertask._robotassessor.RobotAssessor import RobotAssessor  # noqa
from spideriment_ng.worker.workertask._normalizers.NormalizerFactory import NormalizerFactory  # noqa
from spideriment_ng.worker.workertask._normalizers.URLNormalizer import URLNormalizer  # noqa
from spideriment_ng.worker.workertask._normalizers.exc.NormalizerBaseExc import NormalizerBaseExc  # noqa
from spideriment_ng.worker.workertask._crawler.Crawler import Crawler  # noqa


class WorkerTaskMain:
    def __init__(self):
        self._database_module_adapter: Final[DatabaseModuleAdapter] = DatabaseModuleAdapter()

        normalizer_factory = NormalizerFactory()
        self._url_normalizer: Final[URLNormalizer] = normalizer_factory.generate_url_normalizer_using_program_config()

        self._crawler: Final[Crawler] = Crawler(
            database_module_adapter=self._database_module_adapter,
            robot_assessor=RobotAssessor(),
            url_normalizer=self._url_normalizer,
            document_normalizer=normalizer_factory.generate_document_normalizer_using_program_config()
        )

    @WORKER_DI_NS.inject_dependencies("termination_flag_carrier", "logger")
    async def main(self, worker_task_id: int, termination_flag_carrier: FlagCarrier, logger: Logger) -> None:
        logger.log(LogSeverity.DEBUG, f"Worker task with ID {worker_task_id} has started.")

        await self._announce_start_urls()
        self._force_garbage_collection_if_desired()  # Memory saving

        # Crawling loop ("infinite")
        while not termination_flag_carrier.get():
            await self._crawler.crawl_one_document()
            self._force_garbage_collection_if_desired()  # Memory saving

        logger.log(LogSeverity.DEBUG, f"Worker task with ID {worker_task_id} is terminating...")

    @WORKER_DI_NS.inject_dependencies("configuration")
    def _force_garbage_collection_if_desired(self, configuration: Configuration) -> None:
        if configuration.get_generic_configuration().get_force_garbage_collection():
            gc.collect()

    @WORKER_DI_NS.inject_dependencies("configuration")
    async def _announce_start_urls(self, configuration: Configuration) -> None:
        validated_absolute_start_urls = self._normalize_and_ensure_uniqueness_of_start_urls(
            start_urls=configuration.get_generic_configuration().get_start_urls()
        )

        await self._database_module_adapter.announce_start_urls(
            validated_absolute_start_urls=validated_absolute_start_urls
        )

    def _normalize_and_ensure_uniqueness_of_start_urls(self, start_urls: Sequence[urllib.parse.ParseResult]) -> Sequence[URLContainer]:
        urls_already_present = set()
        validated_absolute_start_urls = []

        for start_url in start_urls:
            start_url_string = urllib.parse.urlunparse(start_url)
            try:
                validated_absolute_start_url = self._url_normalizer.use_on_absolute_url(URLContainer(
                    validated=False,
                    certainly_absolute=True,
                    url=start_url_string
                ))
            except NormalizerBaseExc:
                raise InvalidStartURLExc(start_url_string)

            validated_absolute_start_url_string = validated_absolute_start_url.get_url()
            if validated_absolute_start_url_string in urls_already_present:
                continue  # Ensuring uniqueness of URLs

            urls_already_present.add(validated_absolute_start_url_string)
            validated_absolute_start_urls.append(validated_absolute_start_url)

        if len(validated_absolute_start_urls) < 1:
            raise NoStartURLsExc()

        return validated_absolute_start_urls
