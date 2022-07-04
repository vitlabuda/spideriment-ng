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
from typing import Final, List
from spideriment_ng.config.ConfiguredModule import ConfiguredModule
from spideriment_ng.modules.ModuleIface import ModuleIface
from spideriment_ng.modules.exc.ModuleBaseExc import ModuleBaseExc
from spideriment_ng.worker.modulect.exc.FailedToDestroyModuleInstancesExc import FailedToDestroyModuleInstancesExc


class ModuleInstanceCaretaker:
    # Instantiates modules according to supplied configuration objects and makes sure that the instances are always destroyed.

    def __init__(self, instance_name: str):
        self._instance_name: Final[str] = instance_name
        self._caretaken_instances: Final[List[ModuleIface]] = []
        self._entered: bool = False

    async def __aenter__(self) -> ModuleInstanceCaretaker:
        assert (not self._entered)
        self._entered = True

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        assert self._entered

        caught_exceptions = []
        for instance in self._caretaken_instances:
            try:
                await instance.destroy_instance()
            except ModuleBaseExc as e:
                caught_exceptions.append(e)

        self._caretaken_instances.clear()
        self._entered = False

        if caught_exceptions:
            raise FailedToDestroyModuleInstancesExc(caught_exceptions)  # Since multiple exceptions cannot be raised directly, they are wrapped inside this exception

    async def take_care_of(self, module_configuration: ConfiguredModule) -> ModuleIface:
        assert self._entered

        # If an exception is raised while creating the instance, it is propagated up the call stack (in this case, there is no need to wrap it inside another exception)
        instance = await module_configuration.get_module_class().create_instance(module_configuration.get_module_options(), self._instance_name)

        self._caretaken_instances.append(instance)
        return instance
