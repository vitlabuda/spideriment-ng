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


from typing import Final, Sequence
import re
from spideriment_ng.config.FilterRule import FilterRule
from spideriment_ng.helpers.containers.document.DocumentContainer import DocumentContainer
from spideriment_ng.helpers.containers.document.URLContainer import URLContainer
from spideriment_ng.helpers.containers.document.ContentSnippetContainer import ContentSnippetContainer
from spideriment_ng.helpers.containers.document.LinkContainer import LinkContainer
from spideriment_ng.helpers.containers.document.ImageContainer import ImageContainer
from spideriment_ng.worker.workertask._normalizers.URLNormalizer import URLNormalizer
from spideriment_ng.worker.workertask._normalizers.TextNormalizer import TextNormalizer
from spideriment_ng.worker.workertask._normalizers._FilterRuleChecker import _FilterRuleChecker
from spideriment_ng.worker.workertask._normalizers.exc.NormalizerBaseExc import NormalizerBaseExc
from spideriment_ng.worker.workertask._normalizers.exc.InvalidFileTypeExc import InvalidFileTypeExc
from spideriment_ng.worker.workertask._normalizers.exc.TextBlockedByFilterRuleExc import TextBlockedByFilterRuleExc


class DocumentNormalizer:
    def __init__(self, title_normalizer: TextNormalizer, description_normalizer: TextNormalizer, keyword_normalizer: TextNormalizer,
                 max_keywords: int, language_filter_rules: Sequence[FilterRule], author_normalizer: TextNormalizer,
                 content_snippet_normalizer: TextNormalizer, max_content_snippets: int, max_content_snippets_per_type: int,
                 link_href_url_normalizer: URLNormalizer, link_text_normalizer: TextNormalizer, max_links: int,
                 image_src_url_normalizer: URLNormalizer, image_alt_text_normalizer: TextNormalizer, image_title_text_normalizer: TextNormalizer,
                 max_images: int):
        assert (max_keywords > 0)
        assert (max_content_snippets > 0)
        assert (max_content_snippets_per_type > 0)
        assert (max_links > 0)
        assert (max_images > 0)

        self._title_normalizer: Final[TextNormalizer] = title_normalizer
        self._description_normalizer: Final[TextNormalizer] = description_normalizer
        self._keyword_normalizer: Final[TextNormalizer] = keyword_normalizer
        self._max_keywords: Final[int] = max_keywords
        self._language_filter_rule_checker: Final[_FilterRuleChecker] = _FilterRuleChecker(language_filter_rules)
        self._author_normalizer: Final[TextNormalizer] = author_normalizer
        self._content_snippet_normalizer: Final[TextNormalizer] = content_snippet_normalizer
        self._max_content_snippets: Final[int] = max_content_snippets
        self._max_content_snippets_per_type: Final[int] = max_content_snippets_per_type
        self._link_href_url_normalizer: Final[URLNormalizer] = link_href_url_normalizer
        self._link_text_normalizer: Final[TextNormalizer] = link_text_normalizer
        self._max_links: Final[int] = max_links
        self._image_src_url_normalizer: Final[URLNormalizer] = image_src_url_normalizer
        self._image_alt_text_normalizer: Final[TextNormalizer] = image_alt_text_normalizer
        self._image_title_text_normalizer: Final[TextNormalizer] = image_title_text_normalizer
        self._max_images: Final[int] = max_images

    def use(self, validated_absolute_document_url: URLContainer, unvalidated_document: DocumentContainer) -> DocumentContainer:
        """
        :raises NormalizerBaseExc
        """

        assert (validated_absolute_document_url.is_validated() and validated_absolute_document_url.is_certainly_absolute())
        assert (not unvalidated_document.is_validated())
        for content_snippet in unvalidated_document.get_content_snippets():
            assert (not content_snippet.is_validated())
        for link in unvalidated_document.get_links():
            assert (not link.is_validated())
            assert (not link.get_href_url().is_validated())
        for image in unvalidated_document.get_images():
            assert (not image.is_validated())
            assert (not image.get_src_url().is_validated())

        return DocumentContainer(
            validated=True,
            file_type=self._normalize_file_type(unvalidated_document.get_file_type()),
            title=self._normalize_title(unvalidated_document.get_title()),
            description=self._normalize_description(unvalidated_document.get_description()),
            keywords=self._normalize_keywords(unvalidated_document.get_keywords()),
            language=self._normalize_language(unvalidated_document.get_language()),
            author=self._normalize_author(unvalidated_document.get_author()),
            content_snippets=self._normalize_content_snippets(unvalidated_document.get_content_snippets()),
            links=self._normalize_links(unvalidated_document.get_links(), validated_absolute_document_url),
            images=self._normalize_images(unvalidated_document.get_images(), validated_absolute_document_url)
        )

    def _normalize_file_type(self, initial_file_type: str) -> str:
        new_file_type = initial_file_type.strip().lower()

        if re.match(r'^[0-9a-z._-]{1,24}\Z', new_file_type):
            return new_file_type

        raise InvalidFileTypeExc(new_file_type)

    def _normalize_title(self, initial_title: str) -> str:
        return self._title_normalizer.use(initial_title)

    def _normalize_description(self, initial_description: str) -> str:
        return self._description_normalizer.use(initial_description)

    def _normalize_keywords(self, initial_keywords: Sequence[str]) -> Sequence[str]:
        # Keywords are case-insensitive & must be unique per-document (ensured by the set)
        new_keywords_set = set(self._keyword_normalizer.use(initial_keyword).lower() for initial_keyword in initial_keywords)
        new_keywords_set.discard("")  # "Empty" keywords are meaningless

        return tuple(new_keywords_set)[0:self._max_keywords]

    def _normalize_language(self, initial_language: str) -> str:
        new_language = initial_language.strip().lower().replace("_", "-")

        if not self._language_filter_rule_checker.check_string(new_language):
            raise TextBlockedByFilterRuleExc(new_language)

        # If 'new_language' is an empty string, the regex match fails, but the empty string is then returned below (as it should)!
        if re.match(r'^[0-9a-z-]{2,24}\Z', new_language) and (not new_language.startswith("-")) and (not new_language.endswith("-")):
            return new_language

        return ""  # Empty language means "unknown"

    def _normalize_author(self, initial_author: str) -> str:
        return self._author_normalizer.use(initial_author).title()

    def _normalize_content_snippets(self, initial_content_snippets: Sequence[ContentSnippetContainer]) -> Sequence[ContentSnippetContainer]:
        # Not the most optimized piece of code, but relatively straightforward.

        # Iterate through the supplied content snippets, normalize their texts and filter out the ones whose texts are
        #  empty, add the normalized texts into sets (which make sure that the texts are unique per snippet type)
        #  corresponding to their snippet types
        new_content_snippets_dict = dict()  # (snippet type) -> (set of snippet texts)
        for initial_content_snippet in initial_content_snippets:
            new_text = self._content_snippet_normalizer.use(initial_content_snippet.get_snippet_text())
            if not new_text:
                continue

            snippet_type = initial_content_snippet.get_snippet_type()
            if snippet_type in new_content_snippets_dict:
                new_content_snippets_dict[snippet_type].add(new_text)
            else:
                new_content_snippets_dict[snippet_type] = {new_text}

        # Limit the number of content snippets per snippet type and put them into validated containers
        new_content_snippets = []
        for snippet_type, snippet_texts in new_content_snippets_dict.items():
            new_content_snippets += [
                ContentSnippetContainer(validated=True, snippet_type=snippet_type, snippet_text=snippet_text)
                for snippet_text in tuple(snippet_texts)[0:self._max_content_snippets_per_type]  # Sets are not subscriptable
            ]

        # Limit the total number of content snippets and return them
        return new_content_snippets[0:self._max_content_snippets]

    def _normalize_links(self, initial_links: Sequence[LinkContainer], validated_absolute_document_url: URLContainer) -> Sequence[LinkContainer]:
        # This function could also be implemented using a dictionary instead of a set and a list.
        urls_already_present = set()  # Lookups in sets have O(1) time complexity (at least in CPython, where they are implemented as hash tables)
        new_links = []

        for initial_link in initial_links:
            if len(new_links) >= self._max_links:
                break

            try:
                new_href_url = self._link_href_url_normalizer.use_on_possibly_relative_url(
                    validated_absolute_base_url=validated_absolute_document_url,
                    unvalidated_nonabsolute_url=initial_link.get_href_url()
                )
            except NormalizerBaseExc:
                continue  # Invalid links are ignored

            new_href_url_string = new_href_url.get_url()
            if new_href_url_string in urls_already_present:
                continue  # Ensuring uniqueness of URLs

            try:
                new_link_text = self._link_text_normalizer.use(initial_link.get_link_text())
            except NormalizerBaseExc:
                continue  # Invalid links are ignored

            urls_already_present.add(new_href_url_string)
            new_links.append(LinkContainer(
                validated=True,
                href_url=new_href_url,
                link_text=new_link_text
            ))

        return new_links

    def _normalize_images(self, initial_images: Sequence[ImageContainer], validated_absolute_document_url: URLContainer) -> Sequence[ImageContainer]:
        # This function could also be implemented using a dictionary instead of a set and a list.
        urls_already_present = set()  # Lookups in sets have O(1) time complexity (at least in CPython, where they are implemented as hash tables)
        new_images = []

        for initial_image in initial_images:
            if len(new_images) >= self._max_images:
                break

            try:
                new_src_url = self._image_src_url_normalizer.use_on_possibly_relative_url(
                    validated_absolute_base_url=validated_absolute_document_url,
                    unvalidated_nonabsolute_url=initial_image.get_src_url()
                )
            except NormalizerBaseExc:
                continue  # Invalid images are ignored

            new_src_url_string = new_src_url.get_url()
            if new_src_url_string in urls_already_present:
                continue  # Ensuring uniqueness of URLs

            try:
                new_alt_text = self._image_alt_text_normalizer.use(initial_image.get_alt_text())
                new_title_text = self._image_title_text_normalizer.use(initial_image.get_title_text())
            except NormalizerBaseExc:
                continue  # Invalid images are ignored

            urls_already_present.add(new_src_url_string)
            new_images.append(ImageContainer(
                validated=True,
                src_url=new_src_url,
                alt_text=new_alt_text,
                title_text=new_title_text
            ))

        return new_images
