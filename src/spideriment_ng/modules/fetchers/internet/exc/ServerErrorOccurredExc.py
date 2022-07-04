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


from typing import Final
from spideriment_ng.modules.fetchers.exc.FetcherModuleExcType import FetcherModuleExcType
from spideriment_ng.modules.fetchers.internet.exc.InternetFetcherModuleBaseExc import InternetFetcherModuleBaseExc


class ServerErrorOccurredExc(InternetFetcherModuleBaseExc):
    def __init__(self, http_response_code: int):
        InternetFetcherModuleBaseExc.__init__(self, f"A '{http_response_code}' HTTP server error occurred while trying to fetch the supplied URL!", self._get_exception_type_by_http_response_code(http_response_code), None)

        self._http_response_code: Final[int] = http_response_code

    def _get_exception_type_by_http_response_code(self, http_response_code: int) -> FetcherModuleExcType:
        return ({
            401: FetcherModuleExcType.FORBIDDEN,
            403: FetcherModuleExcType.FORBIDDEN,
            404: FetcherModuleExcType.NOT_FOUND,
            451: FetcherModuleExcType.FORBIDDEN
        }.get(http_response_code, FetcherModuleExcType.SERVER_ERROR))

    def get_http_response_code(self) -> int:
        return self._http_response_code
