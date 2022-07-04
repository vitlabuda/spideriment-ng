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


from spideriment_ng.SpiderimentConstants import SpiderimentConstants
from spideriment_ng.logger.LogSeverity import LogSeverity
from spideriment_ng.supervisor.configload.ConfigurationLoader import ConfigurationLoader
from spideriment_ng.supervisor.di import SUPERVISOR_DI_NS
from spideriment_ng.supervisor.di.SupervisorDependencyProvider import SupervisorDependencyProvider
from spideriment_ng.supervisor.workerprocct.WorkerProcessCaretaker import WorkerProcessCaretaker


class SupervisorMain:
    def main(self, config_file_path: str) -> None:
        configuration = ConfigurationLoader().load_configuration_from_toml_file(config_file_path)

        print_debug_log_messages = configuration.get_generic_configuration().get_print_debug_log_messages()
        with SpiderimentConstants.LOGGER_FACTORY.acquire_logger_instance_for_supervisor_process(print_debug_log_messages) as logger:
            logger.log(LogSeverity.DEBUG, "Supervisor process started and is now initializing.")

            dependency_provider = SupervisorDependencyProvider(configuration, logger)
            SUPERVISOR_DI_NS.set_dependency_provider(dependency_provider)

            logger.log(LogSeverity.DEBUG, "Supervisor process initialized successfully!")

            WorkerProcessCaretaker().run()

            logger.log(LogSeverity.DEBUG, "Supervisor process is now terminating.")
