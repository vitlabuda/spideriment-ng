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


from typing import final, Final, Dict
from spideriment_ng.helpers.UninstantiableClassMixin import UninstantiableClassMixin
from spideriment_ng.helpers.CrawlingErrorReason import CrawlingErrorReason
from spideriment_ng.helpers.containers.document.ContentSnippetType import ContentSnippetType


@final
class EnumValues(UninstantiableClassMixin):
    # Must not be mutated!
    _CONTENT_SNIPPET_TYPE: Final[Dict[ContentSnippetType, str]] = {
        ContentSnippetType.HEADING_1: "heading_1",
        ContentSnippetType.HEADING_2: "heading_2",
        ContentSnippetType.HEADING_3: "heading_3",
        ContentSnippetType.HEADING_4: "heading_4",
        ContentSnippetType.HEADING_5: "heading_5",
        ContentSnippetType.EMPHASIZED_TEXT: "emphasized_text",
        ContentSnippetType.REGULAR_TEXT: "regular_text",
        ContentSnippetType.LIST_ITEM_TEXT: "list_item_text",
        ContentSnippetType.UNCATEGORIZED_TEXT: "uncategorized_text",
        ContentSnippetType.FALLBACK_TEXT: "fallback_text"
    }

    # Must not be mutated!
    _LINK_CRAWLING_ERROR_REASON: Final[Dict[CrawlingErrorReason, str]] = {
        CrawlingErrorReason.FETCH_CONNECTION_ERROR:         "fetch_connection_error",
        CrawlingErrorReason.FETCH_NOT_FOUND:                "fetch_not_found",
        CrawlingErrorReason.FETCH_FORBIDDEN:                "fetch_forbidden",
        CrawlingErrorReason.FETCH_SERVER_ERROR:             "fetch_server_error",
        CrawlingErrorReason.FETCH_TOO_MANY_REDIRECTS:       "fetch_too_many_redirects",
        CrawlingErrorReason.FETCH_UNCATEGORIZED_ERROR:      "fetch_uncategorized_error",

        CrawlingErrorReason.ROBOTS_FORBIDDEN:               "robots_forbidden",
        CrawlingErrorReason.ROBOTS_DELAY_TOO_LONG:          "robots_delay_too_long",
        CrawlingErrorReason.ROBOTS_UNCATEGORIZED_ERROR:     "robots_uncategorized_error",

        CrawlingErrorReason.PARSE_UNSUPPORTED_TYPE:         "parse_unsupported_type",
        CrawlingErrorReason.PARSE_CUT_OFF_CONTENT:          "parse_cut_off_content",
        CrawlingErrorReason.PARSE_INVALID_FORMAT:           "parse_invalid_format",
        CrawlingErrorReason.PARSE_INVALID_CONTENT:          "parse_invalid_content",
        CrawlingErrorReason.PARSE_FORBIDDEN:                "parse_forbidden",
        CrawlingErrorReason.PARSE_UNCATEGORIZED_ERROR:      "parse_uncategorized_error",

        CrawlingErrorReason.VALIDATION_URL_PROBLEM:         "validation_url_problem",
        CrawlingErrorReason.VALIDATION_DOCUMENT_PROBLEM:    "validation_document_problem",
        CrawlingErrorReason.VALIDATION_UNCATEGORIZED_ERROR: "validation_uncategorized_error",

        CrawlingErrorReason.FINAL_URL_NOT_CRAWLABLE:        "final_url_not_crawlable",
        CrawlingErrorReason.UNCATEGORIZED_ERROR:            "uncategorized_error",
        CrawlingErrorReason.UNKNOWN_ERROR:                  "unknown_error"
    }

    @classmethod  # Getter method which prevents the dictionary from being mutated.
    def get_content_snippet_type(cls, enum_key: ContentSnippetType) -> str:
        return cls._CONTENT_SNIPPET_TYPE[enum_key]

    @classmethod  # Getter method which prevents the dictionary from being mutated.
    def get_link_crawling_error_reason(cls, enum_key: CrawlingErrorReason) -> str:
        return cls._LINK_CRAWLING_ERROR_REASON[enum_key]
