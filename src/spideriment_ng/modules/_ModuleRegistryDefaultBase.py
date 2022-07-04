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


from typing import Sequence, Mapping, Type
import abc
from spideriment_ng.helpers.UninstantiableClassMixin import UninstantiableClassMixin
from spideriment_ng.modules.ModuleIface import ModuleIface
from spideriment_ng.modules.ModuleRegistryIface import ModuleRegistryIface
from spideriment_ng.modules.exc.ModuleNotFoundInRegistryExc import ModuleNotFoundInRegistryExc


class _ModuleRegistryDefaultBase(ModuleRegistryIface, UninstantiableClassMixin, metaclass=abc.ABCMeta):
    @classmethod
    def get_all_modules(cls) -> Mapping[str, Type[ModuleIface]]:
        return {module_class.get_module_info().get_name(): module_class for module_class in cls._get_all_module_classes()}

    @classmethod
    def get_module_by_name(cls, name: str) -> Type[ModuleIface]:
        try:
            return cls.get_all_modules()[name]
        except KeyError:
            raise ModuleNotFoundInRegistryExc(name)

    @classmethod
    @abc.abstractmethod
    def _get_all_module_classes(cls) -> Sequence[Type[ModuleIface]]:
        raise NotImplementedError(cls._get_all_module_classes.__qualname__)
