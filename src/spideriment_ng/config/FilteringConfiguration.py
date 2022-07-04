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


from typing import Final, Sequence, Tuple
import re
from spideriment_ng.config.FilterRule import FilterRule


class FilteringConfiguration:
    def __init__(self, url_filters: Sequence[FilterRule], url_host_filters: Sequence[FilterRule],
                 url_path_filters: Sequence[FilterRule], url_query_filters: Sequence[FilterRule],
                 title_filters: Sequence[FilterRule], description_filters: Sequence[FilterRule],
                 keyword_filters: Sequence[FilterRule], language_filters: Sequence[FilterRule],
                 author_filters: Sequence[FilterRule], content_snippet_filters: Sequence[FilterRule],
                 link_text_filters: Sequence[FilterRule], img_url_filters: Sequence[FilterRule],
                 img_url_host_filters: Sequence[FilterRule], img_url_path_filters: Sequence[FilterRule],
                 img_url_query_filters: Sequence[FilterRule], img_alt_text_filters: Sequence[FilterRule],
                 img_title_filters: Sequence[FilterRule], remove_query_parameters_matching_regex: Sequence[re.Pattern],
                 allow_nonstandard_ports: bool):

        for pattern in remove_query_parameters_matching_regex:
            assert ((int(pattern.flags) & int(re.IGNORECASE)) != 0)

        self._url_filters: Final[Tuple[FilterRule, ...]] = tuple(url_filters)
        self._url_host_filters: Final[Tuple[FilterRule, ...]] = tuple(url_host_filters)
        self._url_path_filters: Final[Tuple[FilterRule, ...]] = tuple(url_path_filters)
        self._url_query_filters: Final[Tuple[FilterRule, ...]] = tuple(url_query_filters)
        self._title_filters: Final[Tuple[FilterRule, ...]] = tuple(title_filters)
        self._description_filters: Final[Tuple[FilterRule, ...]] = tuple(description_filters)
        self._keyword_filters: Final[Tuple[FilterRule, ...]] = tuple(keyword_filters)
        self._language_filters: Final[Tuple[FilterRule, ...]] = tuple(language_filters)
        self._author_filters: Final[Tuple[FilterRule, ...]] = tuple(author_filters)
        self._content_snippet_filters: Final[Tuple[FilterRule, ...]] = tuple(content_snippet_filters)
        self._link_text_filters: Final[Tuple[FilterRule, ...]] = tuple(link_text_filters)

        self._img_url_filters: Final[Tuple[FilterRule, ...]] = tuple(img_url_filters)
        self._img_url_host_filters: Final[Tuple[FilterRule, ...]] = tuple(img_url_host_filters)
        self._img_url_path_filters: Final[Tuple[FilterRule, ...]] = tuple(img_url_path_filters)
        self._img_url_query_filters: Final[Tuple[FilterRule, ...]] = tuple(img_url_query_filters)
        self._img_alt_text_filters: Final[Tuple[FilterRule, ...]] = tuple(img_alt_text_filters)
        self._img_title_filters: Final[Tuple[FilterRule, ...]] = tuple(img_title_filters)

        self._remove_query_parameters_matching_regex: Final[Tuple[re.Pattern, ...]] = tuple(remove_query_parameters_matching_regex)
        self._allow_nonstandard_ports: Final[bool] = allow_nonstandard_ports

    def get_url_filters(self) -> Sequence[FilterRule]:
        return self._url_filters

    def get_url_host_filters(self) -> Sequence[FilterRule]:
        return self._url_host_filters

    def get_url_path_filters(self) -> Sequence[FilterRule]:
        return self._url_path_filters

    def get_url_query_filters(self) -> Sequence[FilterRule]:
        return self._url_query_filters

    def get_title_filters(self) -> Sequence[FilterRule]:
        return self._title_filters

    def get_description_filters(self) -> Sequence[FilterRule]:
        return self._description_filters

    def get_keyword_filters(self) -> Sequence[FilterRule]:
        return self._keyword_filters

    def get_language_filters(self) -> Sequence[FilterRule]:
        return self._language_filters

    def get_author_filters(self) -> Sequence[FilterRule]:
        return self._author_filters

    def get_content_snippet_filters(self) -> Sequence[FilterRule]:
        return self._content_snippet_filters

    def get_link_text_filters(self) -> Sequence[FilterRule]:
        return self._link_text_filters

    def get_img_url_filters(self) -> Sequence[FilterRule]:
        return self._img_url_filters

    def get_img_url_host_filters(self) -> Sequence[FilterRule]:
        return self._img_url_host_filters

    def get_img_url_path_filters(self) -> Sequence[FilterRule]:
        return self._img_url_path_filters

    def get_img_url_query_filters(self) -> Sequence[FilterRule]:
        return self._img_url_query_filters

    def get_img_alt_text_filters(self) -> Sequence[FilterRule]:
        return self._img_alt_text_filters

    def get_img_title_filters(self) -> Sequence[FilterRule]:
        return self._img_title_filters

    def get_remove_query_parameters_matching_regex(self) -> Sequence[re.Pattern]:
        return self._remove_query_parameters_matching_regex

    def get_allow_nonstandard_ports(self) -> bool:
        return self._allow_nonstandard_ports
