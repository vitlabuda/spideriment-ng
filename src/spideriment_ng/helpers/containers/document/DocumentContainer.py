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
from ._DocumentContainerBase import _DocumentContainerBase
from .ContentSnippetContainer import ContentSnippetContainer
from .LinkContainer import LinkContainer
from .ImageContainer import ImageContainer


class DocumentContainer(_DocumentContainerBase):
    def __init__(self, validated: bool, file_type: str, title: str, description: str, keywords: Sequence[str], language: str, author: str,
                 content_snippets: Sequence[ContentSnippetContainer], links: Sequence[LinkContainer], images: Sequence[ImageContainer]):

        _DocumentContainerBase.__init__(self, validated)

        assert (len(file_type) > 0)

        self._file_type: Final[str] = file_type
        self._title: Final[str] = title
        self._description: Final[str] = description
        self._keywords: Final[Tuple[str, ...]] = tuple(keywords)
        self._language: Final[str] = language
        self._author: Final[str] = author
        self._content_snippets: Final[Tuple[ContentSnippetContainer, ...]] = tuple(content_snippets)
        self._links: Final[Tuple[LinkContainer, ...]] = tuple(links)
        self._images: Final[Tuple[ImageContainer, ...]] = tuple(images)

        # Mixing validated and non-validated data is not a good idea!
        for validatable_item in (self._content_snippets + self._links + self._images):
            assert (validatable_item.is_validated() == validated)

    def get_file_type(self) -> str:
        return self._file_type

    def get_title(self) -> str:
        return self._title

    def get_description(self) -> str:
        return self._description

    def get_keywords(self) -> Sequence[str]:
        return self._keywords

    def get_language(self) -> str:
        return self._language

    def get_author(self) -> str:
        return self._author

    def get_content_snippets(self) -> Sequence[ContentSnippetContainer]:
        return self._content_snippets

    def get_links(self) -> Sequence[LinkContainer]:
        return self._links

    def get_images(self) -> Sequence[ImageContainer]:
        return self._images
