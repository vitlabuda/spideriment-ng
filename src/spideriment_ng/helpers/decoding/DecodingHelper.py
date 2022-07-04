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
import codecs
import chardet
from .exc.FailedToDecodeBinaryDataExc import FailedToDecodeBinaryDataExc
from .exc.UnknownEncodingExc import UnknownEncodingExc
from .exc.FailedToDetectEncodingExc import FailedToDetectEncodingExc


class DecodingHelper:
    _CHARDET_MINIMUM_ACCEPTABLE_CONFIDENCE: Final[float] = 0.2

    def try_detecting_encoding_and_try_decoding_data_using_it(self, binary_data: bytes) -> str:
        detected_encoding = self._automatically_detect_encoding(binary_data)
        return self.validate_encoding_and_try_decoding_data_using_it(binary_data, detected_encoding)

    def validate_encoding_and_try_decoding_data_using_it(self, binary_data: bytes, encoding_name: str) -> str:
        encoding_name = self._normalize_encoding_name(encoding_name)
        self._validate_encoding_name(encoding_name)
        return self.try_decoding_data_using_encoding(binary_data, encoding_name, ignore_errors=False)

    def try_decoding_data_using_encoding(self, binary_data: bytes, encoding_name: str, ignore_errors: bool) -> str:
        errors = ("ignore" if ignore_errors else "strict")

        try:
            return binary_data.decode(encoding_name, errors)
        except UnicodeError:
            raise FailedToDecodeBinaryDataExc(encoding_name)

    def _normalize_encoding_name(self, encoding_name: str) -> str:
        return encoding_name.strip().lower()

    def _validate_encoding_name(self, encoding_name: str) -> None:
        try:
            codecs.lookup(encoding_name)
        except LookupError:
            raise UnknownEncodingExc(encoding_name)

    def _automatically_detect_encoding(self, binary_data: bytes) -> str:
        chardet_result = chardet.detect(binary_data)

        if (chardet_result["encoding"] is None) or (chardet_result["confidence"] < self.__class__._CHARDET_MINIMUM_ACCEPTABLE_CONFIDENCE):
            raise FailedToDetectEncodingExc()

        return chardet_result["encoding"]
