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


import enum


class CrawlingErrorReason(enum.Enum):
    FETCH_CONNECTION_ERROR = 10
    FETCH_NOT_FOUND = 20
    FETCH_FORBIDDEN = 30
    FETCH_SERVER_ERROR = 40
    FETCH_TOO_MANY_REDIRECTS = 50
    FETCH_UNCATEGORIZED_ERROR = 60

    ROBOTS_FORBIDDEN = 70
    ROBOTS_DELAY_TOO_LONG = 80
    ROBOTS_UNCATEGORIZED_ERROR = 90

    PARSE_UNSUPPORTED_TYPE = 100
    PARSE_CUT_OFF_CONTENT = 110
    PARSE_INVALID_FORMAT = 120
    PARSE_INVALID_CONTENT = 130
    PARSE_FORBIDDEN = 140
    PARSE_UNCATEGORIZED_ERROR = 150

    VALIDATION_URL_PROBLEM = 160
    VALIDATION_DOCUMENT_PROBLEM = 170
    VALIDATION_UNCATEGORIZED_ERROR = 180

    FINAL_URL_NOT_CRAWLABLE = 190
    UNCATEGORIZED_ERROR = 200
    UNKNOWN_ERROR = 210
