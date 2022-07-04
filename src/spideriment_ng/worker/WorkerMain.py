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


from typing import Sequence
import signal
import asyncio
from spideriment_ng.SpiderimentConstants import SpiderimentConstants
from spideriment_ng.config.Configuration import Configuration
from spideriment_ng.config.ConfiguredModule import ConfiguredModule
from spideriment_ng.logger.Logger import Logger
from spideriment_ng.logger.LogSeverity import LogSeverity
from spideriment_ng.modules.ModuleIface import ModuleIface
from spideriment_ng.helpers.FlagCarrier import FlagCarrier
from spideriment_ng.worker.modulect.ModuleInstanceCaretaker import ModuleInstanceCaretaker
from spideriment_ng.worker.di import WORKER_DI_NS
from spideriment_ng.worker.di.WorkerDependencyProvider import WorkerDependencyProvider
from spideriment_ng.worker.workertaskct.WorkerTaskCaretaker import WorkerTaskCaretaker


class WorkerMain:
    def main(self, worker_process_id: int, configuration: Configuration) -> None:
        asyncio.run(self._async_main(worker_process_id, configuration))

    async def _async_main(self, worker_process_id: int, configuration: Configuration) -> None:
        termination_flag_carrier = self._set_signal_handlers_for_worker_process()

        print_debug_log_messages = configuration.get_generic_configuration().get_print_debug_log_messages()
        with SpiderimentConstants.LOGGER_FACTORY.acquire_logger_instance_for_worker_process(print_debug_log_messages, worker_process_id) as logger:
            logger.log(LogSeverity.DEBUG, "Worker process started and is now initializing.")
            async with ModuleInstanceCaretaker(configuration.get_generic_configuration().get_instance_name()) as caretaker:
                fetcher = await self._instantiate_module_as_per_configuration(configuration.get_fetcher_module(), caretaker, logger)
                database = await self._instantiate_module_as_per_configuration(configuration.get_database_module(), caretaker, logger)
                ordered_document_parsers = await self._instantiate_multiple_modules_as_per_configurations(configuration.get_ordered_document_parser_modules(), caretaker, logger)
                ordered_robot_caches = await self._instantiate_multiple_modules_as_per_configurations(configuration.get_ordered_robot_cache_modules(), caretaker, logger)

                dependency_provider = WorkerDependencyProvider(worker_process_id, configuration, termination_flag_carrier, logger, fetcher, database, ordered_document_parsers, ordered_robot_caches)  # noqa
                WORKER_DI_NS.set_dependency_provider(dependency_provider)

                logger.log(LogSeverity.DEBUG, "Worker process initialized successfully!")

                await WorkerTaskCaretaker().run()

            logger.log(LogSeverity.DEBUG, "Worker process is now terminating.")

    def _set_signal_handlers_for_worker_process(self) -> FlagCarrier:
        termination_flag_carrier = FlagCarrier(initial_value=False)

        for signum in SpiderimentConstants.PROGRAM_TERMINATION_SIGNALS:
            signal.signal(signum, signal.SIG_IGN)  # These signals are caught only by the supervisor process

        def _worker_signal_handler(ignored1, ignored2):  # noqa
            signal.signal(SpiderimentConstants.WORKER_PROCESS_TERMINATION_SIGNAL, signal.SIG_IGN)  # The signal has been caught and there is no need to catch it again
            termination_flag_carrier.set(True)

        signal.signal(SpiderimentConstants.WORKER_PROCESS_TERMINATION_SIGNAL, _worker_signal_handler)

        return termination_flag_carrier

    async def _instantiate_module_as_per_configuration(self, module_configuration: ConfiguredModule, caretaker: ModuleInstanceCaretaker, logger: Logger) -> ModuleIface:
        module_class = module_configuration.get_module_class()
        module_name = module_class.get_module_info().get_name()

        logger.log(LogSeverity.DEBUG, f"Instantiating module '{module_name}' / {module_class.__name__}...")

        module_instance = await caretaker.take_care_of(module_configuration)  # May raise an exception

        logger.log(LogSeverity.DEBUG, f"Module '{module_name}' / {module_class.__name__} instantiated successfully!")

        return module_instance

    async def _instantiate_multiple_modules_as_per_configurations(self, module_configurations: Sequence[ConfiguredModule], caretaker: ModuleInstanceCaretaker, logger: Logger) -> Sequence[ModuleIface]:
        # The instances are in the same order as the configurations!
        return [(await self._instantiate_module_as_per_configuration(module_configuration, caretaker, logger)) for module_configuration in module_configurations]
