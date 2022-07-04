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


from __future__ import annotations
from typing import Final, Any, Tuple, Optional, Sequence
import re
import bs4
from spideriment_ng.helpers.decoding.DecodingHelper import DecodingHelper
from spideriment_ng.helpers.decoding.exc.DecodingHelperBaseExc import DecodingHelperBaseExc
from spideriment_ng.helpers.containers.FetchedFileContainer import FetchedFileContainer
from spideriment_ng.helpers.containers.document.DocumentContainer import DocumentContainer
from spideriment_ng.helpers.containers.document.LinkContainer import LinkContainer
from spideriment_ng.helpers.containers.document.ImageContainer import ImageContainer
from spideriment_ng.helpers.containers.document.URLContainer import URLContainer
from spideriment_ng.helpers.containers.document.ContentSnippetContainer import ContentSnippetContainer
from spideriment_ng.helpers.containers.document.ContentSnippetType import ContentSnippetType
from spideriment_ng.modules.ModuleInfo import ModuleInfo
from spideriment_ng.modules.ModuleType import ModuleType
from spideriment_ng.modules.documentparsers.DocumentParserModuleIface import DocumentParserModuleIface
from spideriment_ng.modules.documentparsers.html.exc.MIMETypeNotAcceptableForHTMLExc import MIMETypeNotAcceptableForHTMLExc
from spideriment_ng.modules.documentparsers.html.exc.FailedToDecodeHTMLDataExc import FailedToDecodeHTMLDataExc
from spideriment_ng.modules.documentparsers.html.exc.CrawlingForbiddenByRobotsTagExc import CrawlingForbiddenByRobotsTagExc


class HTMLDocumentParserModule(DocumentParserModuleIface):
    class _InternalExc(Exception):
        pass

    _MODULE_INFO: Final[ModuleInfo] = ModuleInfo(
        type_=ModuleType.DOCUMENT_PARSER,
        name="html",
        configuration_blueprint=None  # This module does not have any configuration options
    )

    _FILE_TYPE: Final[str] = "html"
    _BEAUTIFULSOUP_PARSER_LIBRARY: Final[str] = "html.parser"
    _ACCEPTABLE_MIME_TYPES: Final[Tuple[str, ...]] = ("text/html",)
    _FALLBACK_ENCODING: Final[str] = "utf-8"

    _USELESS_HTML_TAGS: Final[Tuple[str, ...]] = ("style", "script")
    _TITLE_TAGS: Final[Tuple[str, ...]] = ("title", "h1", "h2", "h3")  # Beware of the sequence's order!
    _CONTENT_SNIPPET_TAGS: Final[Tuple[Tuple[ContentSnippetType, Tuple[str, ...]], ...]] = (  # dict()s may not preserve order (and are mutable)!
        (ContentSnippetType.HEADING_1,       ("h1",)),
        (ContentSnippetType.HEADING_2,       ("h2",)),
        (ContentSnippetType.HEADING_3,       ("h3",)),
        (ContentSnippetType.HEADING_4,       ("h4",)),
        (ContentSnippetType.HEADING_5,       ("h5",)),
        (ContentSnippetType.EMPHASIZED_TEXT, ("strong", "em")),
        (ContentSnippetType.REGULAR_TEXT,    ("p",)),
        (ContentSnippetType.LIST_ITEM_TEXT,  ("li",)),
    )

    _ROBOTS_TAG_FORBIDS_CRAWLING_REGEX: Final[re.Pattern] = re.compile(r'^.*(noindex|nofollow|none|noarchive).*$', flags=re.IGNORECASE)

    _DEFAULT_TITLE: Final[str] = ""
    _DEFAULT_DESCRIPTION: Final[str] = ""
    _DEFAULT_KEYWORDS: Final[Tuple[str, ...]] = tuple()
    _DEFAULT_LANGUAGE: Final[str] = ""
    _DEFAULT_AUTHOR: Final[str] = ""
    _DEFAULT_CONTENT_SNIPPETS: Final[Tuple[ContentSnippetContainer, ...]] = tuple()
    _DEFAULT_LINKS: Final[Tuple[LinkContainer, ...]] = tuple()
    _DEFAULT_IMAGES: Final[Tuple[ImageContainer, ...]] = tuple()
    _DEFAULT_IMAGE_ALT: Final[str] = ""
    _DEFAULT_IMAGE_TITLE: Final[str] = ""

    @classmethod
    def get_module_info(cls) -> ModuleInfo:
        return cls._MODULE_INFO

    def __init__(self):
        self._decoding_helper: Final[DecodingHelper] = DecodingHelper()
        self._operational: bool = True

    @classmethod
    async def create_instance(cls, module_options: Any, instance_name: str) -> HTMLDocumentParserModule:
        return cls()

    async def destroy_instance(self) -> None:
        assert self._operational
        self._operational = False

    async def parse(self, fetched_file: FetchedFileContainer) -> DocumentContainer:
        assert self._operational

        self._check_mime_type(fetched_file.get_hinted_mime_type())

        string_data = self._decode_binary_data_to_string(fetched_file.get_data(), fetched_file.get_hinted_encoding())
        return self._parse_html_document(string_data)

    def _check_mime_type(self, mime_type: str) -> None:
        mime_type = mime_type.strip().lower()
        if mime_type not in self.__class__._ACCEPTABLE_MIME_TYPES:
            raise MIMETypeNotAcceptableForHTMLExc(mime_type)

    def _decode_binary_data_to_string(self, data: bytes, hinted_encoding: Optional[str]) -> str:
        # HTTP header
        if hinted_encoding is not None:
            try:
                return self._decoding_helper.validate_encoding_and_try_decoding_data_using_it(data, hinted_encoding)
            except DecodingHelperBaseExc:
                pass

        # HTML meta-charset & http-equiv
        temp_decoded_html = bs4.BeautifulSoup(self._decoding_helper.try_decoding_data_using_encoding(data, "ascii", ignore_errors=True), self.__class__._BEAUTIFULSOUP_PARSER_LIBRARY)

        try:
            return self._decoding_helper.validate_encoding_and_try_decoding_data_using_it(data, self._get_meta_charset_from_html(temp_decoded_html))
        except (self.__class__._InternalExc, DecodingHelperBaseExc):
            pass

        try:
            return self._decoding_helper.validate_encoding_and_try_decoding_data_using_it(data, self._get_http_equiv_charset_from_html(temp_decoded_html))
        except (self.__class__._InternalExc, DecodingHelperBaseExc):
            pass

        # Automatic detection
        try:
            return self._decoding_helper.try_detecting_encoding_and_try_decoding_data_using_it(data)
        except DecodingHelperBaseExc:
            pass

        # Fallback
        try:
            return self._decoding_helper.try_decoding_data_using_encoding(data, self.__class__._FALLBACK_ENCODING, ignore_errors=False)
        except DecodingHelperBaseExc:
            raise FailedToDecodeHTMLDataExc()

    def _get_meta_charset_from_html(self, html: bs4.BeautifulSoup) -> str:
        charset_elem = html.find("meta", {"charset": True})
        if charset_elem is None:
            raise self.__class__._InternalExc("Could not find a <meta charset> element!")

        encoding = charset_elem.get("charset", None)
        if encoding is None:
            raise self.__class__._InternalExc("Could not extract the 'charset' attribute from the found <meta charset> element!")

        return encoding.strip()

    def _get_http_equiv_charset_from_html(self, html: bs4.BeautifulSoup) -> str:
        http_equiv_elem = html.find("meta", {"http-equiv": re.compile(r'^Content-Type$', flags=re.IGNORECASE), "content": True})
        if http_equiv_elem is None:
            raise self.__class__._InternalExc("Could not find a <meta http-equiv='Content-Type'> element!")

        content = http_equiv_elem.get("content", None)
        if content is None:
            raise self.__class__._InternalExc("Could not extract the 'content' attribute from the found <meta http-equiv='Content-Type'> element!")

        regex_match = re.match(r'^text/html;\s*charset=(.+)$', content.strip(), flags=re.IGNORECASE)
        if regex_match is None:
            raise self.__class__._InternalExc("Could not extract the charset information from the found <meta http-equiv='Content-Type'> element!")

        return regex_match.group(1).strip()

    def _parse_html_document(self, html_string: str) -> DocumentContainer:
        html = bs4.BeautifulSoup(html_string, self.__class__._BEAUTIFULSOUP_PARSER_LIBRARY)

        self._remove_useless_tags_from_html(html)
        self._check_robots_meta_tag(html)

        return DocumentContainer(
            validated=False,
            file_type=self.__class__._FILE_TYPE,
            title=self._extract_title_from_html(html),
            description=self._extract_description_from_html(html),
            keywords=self._extract_keywords_from_html(html),
            language=self._extract_language_from_html(html),
            author=self._extract_author_from_html(html),
            content_snippets=self._extract_content_snippets_from_html(html),
            links=self._extract_links_from_html(html),
            images=self._extract_images_from_html(html)
        )

    def _remove_useless_tags_from_html(self, html: bs4.BeautifulSoup) -> None:
        for elem in html.find_all(self.__class__._USELESS_HTML_TAGS):
            elem.decompose()

    def _check_robots_meta_tag(self, html: bs4.BeautifulSoup) -> None:
        robots = self._extract_attribute_from_element(html.find("meta", {"name": re.compile(r'^robots$', flags=re.IGNORECASE), "content": True}), "content")
        if robots is not None:
            if self.__class__._ROBOTS_TAG_FORBIDS_CRAWLING_REGEX.search(robots):
                raise CrawlingForbiddenByRobotsTagExc()

    def _extract_title_from_html(self, html: bs4.BeautifulSoup) -> str:
        for tag in self.__class__._TITLE_TAGS:
            title = self._extract_text_from_element(html.find(tag))
            if title is not None:
                return title

        return self.__class__._DEFAULT_TITLE

    def _extract_description_from_html(self, html: bs4.BeautifulSoup) -> str:
        # <meta name='description'>
        description = self._extract_attribute_from_element(html.find("meta", {"name": re.compile(r'^description$', flags=re.IGNORECASE), "content": True}), "content")
        if description is not None:
            return description

        # Fallback - <p>
        description = self._extract_text_from_element(html.find("p"))
        if description is not None:
            return description

        return self.__class__._DEFAULT_DESCRIPTION

    def _extract_keywords_from_html(self, html: bs4.BeautifulSoup) -> Sequence[str]:
        keywords = self._extract_attribute_from_element(html.find("meta", {"name": re.compile(r'^keywords$', flags=re.IGNORECASE), "content": True}), "content")
        if keywords is not None:
            return list(filter(None, map(lambda item: item.strip(), keywords.split(","))))

        return self.__class__._DEFAULT_KEYWORDS

    def _extract_language_from_html(self, html: bs4.BeautifulSoup) -> str:
        language = self._extract_attribute_from_element(html.find("html", {"lang": True}), "lang")
        if language is not None:
            return language

        return self.__class__._DEFAULT_LANGUAGE

    def _extract_author_from_html(self, html: bs4.BeautifulSoup) -> str:
        author = self._extract_attribute_from_element(html.find("meta", {"name": re.compile(r'^author$', flags=re.IGNORECASE), "content": True}), "content")
        if author is not None:
            return author

        return self.__class__._DEFAULT_AUTHOR

    def _extract_content_snippets_from_html(self, html: bs4.BeautifulSoup) -> Sequence[ContentSnippetContainer]:
        snippets = []
        for snippet_type, tags in self.__class__._CONTENT_SNIPPET_TAGS:
            for elem in html.find_all(tags):
                snippet_text = self._extract_text_from_element(elem)
                if snippet_text is not None:
                    snippets.append(ContentSnippetContainer(
                        validated=False,
                        snippet_type=snippet_type,
                        snippet_text=snippet_text
                    ))

        # Fallback
        if len(snippets) == 0:
            fallback_text = self._extract_text_from_element(html)
            if fallback_text is not None:
                snippets.append(ContentSnippetContainer(
                    validated=False,
                    snippet_type=ContentSnippetType.FALLBACK_TEXT,
                    snippet_text=fallback_text
                ))

        if len(snippets) == 0:
            return self.__class__._DEFAULT_CONTENT_SNIPPETS
        return snippets

    def _extract_links_from_html(self, html: bs4.BeautifulSoup) -> Sequence[LinkContainer]:
        links = []
        for elem in html.find_all("a", {"href": True}):
            link_href = self._extract_attribute_from_element(elem, "href")
            link_text = self._extract_text_from_element(elem)
            if (link_href is not None) and (link_text is not None):
                links.append(LinkContainer(
                    validated=False,
                    href_url=URLContainer(validated=False, certainly_absolute=False, url=link_href),
                    link_text=link_text
                ))

        if len(links) == 0:
            return self.__class__._DEFAULT_LINKS
        return links

    def _extract_images_from_html(self, html: bs4.BeautifulSoup) -> Sequence[ImageContainer]:
        images = []
        for elem in html.find_all("img", {"src": True}):
            img_src = self._extract_attribute_from_element(elem, "src")
            if img_src is not None:
                img_alt = self._extract_attribute_from_element(elem, "alt")
                img_title = self._extract_attribute_from_element(elem, "title")
                if img_alt is None:
                    img_alt = self.__class__._DEFAULT_IMAGE_ALT
                if img_title is None:
                    img_title = self.__class__._DEFAULT_IMAGE_TITLE
                images.append(ImageContainer(
                    validated=False,
                    src_url=URLContainer(validated=False, certainly_absolute=False, url=img_src),
                    alt_text=img_alt,
                    title_text=img_title
                ))

        if len(images) == 0:
            return self.__class__._DEFAULT_IMAGES
        return images

    def _extract_text_from_element(self, elem: Optional[bs4.Tag]) -> Optional[str]:
        if elem is not None:
            text = elem.get_text().strip()
            if text:
                return text

        return None

    def _extract_attribute_from_element(self, elem: Optional[bs4.Tag], attr_name: str) -> Optional[str]:
        if elem is not None:
            attribute = elem.get(attr_name, None)
            if attribute is not None:
                attribute = attribute.strip()
                if attribute:
                    return attribute

        return None
