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


from typing import Final, Tuple, Sequence
import urllib.parse


class GenericConfiguration:
    def __init__(self, instance_name: str, print_debug_log_messages: bool, force_garbage_collection: bool, start_urls: Sequence[urllib.parse.ParseResult]):
        self._instance_name: Final[str] = instance_name
        self._print_debug_log_messages: Final[bool] = print_debug_log_messages
        self._force_garbage_collection: Final[bool] = force_garbage_collection
        self._start_urls: Final[Tuple[urllib.parse.ParseResult, ...]] = tuple(start_urls)

    def get_instance_name(self) -> str:
        return self._instance_name

    def get_print_debug_log_messages(self) -> bool:
        return self._print_debug_log_messages

    def get_force_garbage_collection(self) -> bool:
        return self._force_garbage_collection

    def get_start_urls(self) -> Sequence[urllib.parse.ParseResult]:
        return self._start_urls
