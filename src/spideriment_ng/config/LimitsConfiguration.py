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


class LimitsConfiguration:
    def __init__(self, worker_processes: int, worker_tasks_per_process: int, max_document_size: int,
                 max_robots_txt_size: int, request_timeout: int, max_redirects: int, max_crawling_delay: int,
                 url_max_length: int, title_max_length: int, description_max_length: int, keyword_max_length: int,
                 author_max_length: int, content_snippet_max_length: int, link_text_max_length: int,
                 img_alt_text_max_length: int, img_title_max_length: int, max_keywords_per_document: int,
                 max_content_snippets_per_document: int, max_content_snippets_per_type_per_document: int,
                 max_links_per_document: int, max_images_per_document: int):

        self._worker_processes: Final[int] = worker_processes
        self._worker_tasks_per_process: Final[int] = worker_tasks_per_process

        self._max_document_size: Final[int] = max_document_size
        self._max_robots_txt_size: Final[int] = max_robots_txt_size
        self._request_timeout: Final[int] = request_timeout
        self._max_redirects: Final[int] = max_redirects
        self._max_crawling_delay: Final[int] = max_crawling_delay

        self._url_max_length: Final[int] = url_max_length
        self._title_max_length: Final[int] = title_max_length
        self._description_max_length: Final[int] = description_max_length
        self._keyword_max_length: Final[int] = keyword_max_length
        self._author_max_length: Final[int] = author_max_length
        self._content_snippet_max_length: Final[int] = content_snippet_max_length
        self._link_text_max_length: Final[int] = link_text_max_length
        self._img_alt_text_max_length: Final[int] = img_alt_text_max_length
        self._img_title_max_length: Final[int] = img_title_max_length

        self._max_keywords_per_document: Final[int] = max_keywords_per_document
        self._max_content_snippets_per_document: Final[int] = max_content_snippets_per_document
        self._max_content_snippets_per_type_per_document: Final[int] = max_content_snippets_per_type_per_document
        self._max_links_per_document: Final[int] = max_links_per_document
        self._max_images_per_document: Final[int] = max_images_per_document

    def get_worker_processes(self) -> int:
        return self._worker_processes

    def get_worker_tasks_per_process(self) -> int:
        return self._worker_tasks_per_process

    def get_max_document_size(self) -> int:
        return self._max_document_size

    def get_max_robots_txt_size(self) -> int:
        return self._max_robots_txt_size

    def get_request_timeout(self) -> int:
        return self._request_timeout

    def get_max_redirects(self) -> int:
        return self._max_redirects

    def get_max_crawling_delay(self) -> int:
        return self._max_crawling_delay

    def get_url_max_length(self) -> int:
        return self._url_max_length

    def get_title_max_length(self) -> int:
        return self._title_max_length

    def get_description_max_length(self) -> int:
        return self._description_max_length

    def get_keyword_max_length(self) -> int:
        return self._keyword_max_length

    def get_author_max_length(self) -> int:
        return self._author_max_length

    def get_content_snippet_max_length(self) -> int:
        return self._content_snippet_max_length

    def get_link_text_max_length(self) -> int:
        return self._link_text_max_length

    def get_img_alt_text_max_length(self) -> int:
        return self._img_alt_text_max_length

    def get_img_title_max_length(self) -> int:
        return self._img_title_max_length

    def get_max_keywords_per_document(self) -> int:
        return self._max_keywords_per_document

    def get_max_content_snippets_per_document(self) -> int:
        return self._max_content_snippets_per_document

    def get_max_content_snippets_per_type_per_document(self) -> int:
        return self._max_content_snippets_per_type_per_document

    def get_max_links_per_document(self) -> int:
        return self._max_links_per_document

    def get_max_images_per_document(self) -> int:
        return self._max_images_per_document
