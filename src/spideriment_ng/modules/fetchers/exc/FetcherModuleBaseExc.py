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
import abc
from spideriment_ng.helpers.containers.document.URLContainer import URLContainer
from spideriment_ng.modules.exc.ModuleBaseExc import ModuleBaseExc
from spideriment_ng.modules.fetchers.exc.FetcherModuleExcType import FetcherModuleExcType


class FetcherModuleBaseExc(ModuleBaseExc, metaclass=abc.ABCMeta):
    def __init__(self, error_message: str, exception_type: FetcherModuleExcType, unvalidated_nonabsolute_redirect_url: Optional[URLContainer]):
        ModuleBaseExc.__init__(self, error_message)

        if exception_type == FetcherModuleExcType.REDIRECT:
            assert (unvalidated_nonabsolute_redirect_url is not None)
            assert (not unvalidated_nonabsolute_redirect_url.is_validated()) and (not unvalidated_nonabsolute_redirect_url.is_certainly_absolute())
        else:
            assert (unvalidated_nonabsolute_redirect_url is None)

        self._exception_type: Final[FetcherModuleExcType] = exception_type
        self._unvalidated_nonabsolute_redirect_url: Final[Optional[URLContainer]] = unvalidated_nonabsolute_redirect_url

    def get_exception_type(self) -> FetcherModuleExcType:
        return self._exception_type

    def get_unvalidated_nonabsolute_redirect_url(self) -> Optional[URLContainer]:
        return self._unvalidated_nonabsolute_redirect_url
