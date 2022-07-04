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


from typing import final, Final
from spideriment_ng.helpers.UninstantiableClassMixin import UninstantiableClassMixin


@final
class Procedures(UninstantiableClassMixin):
    UNREGISTER_ACTIVE_CRAWLER: Final[str] = "sng_proc__unregister_active_crawler"
    STORE_START_URL_TO_LINKS: Final[str] = "sng_proc__store_start_url_to_links"
    STORE_LINK_TO_CURRENTLY_CRAWLED_LINKS: Final[str] = "sng_proc__store_link_to_currently_crawled_links"
    REMOVE_LINK_FROM_CURRENTLY_CRAWLED_LINKS: Final[str] = "sng_proc__remove_link_from_currently_crawled_links"
    REMOVE_LINK_FROM_LINK_CRAWLING_DELAYS: Final[str] = "sng_proc__remove_link_from_link_crawling_delays"
    FINISH_CRAWLING_WITH_DELAY: Final[str] = "sng_proc__finish_crawling_with_delay"
    FINISH_CRAWLING_WITH_ERROR: Final[str] = "sng_proc__finish_crawling_with_error"
    ADD_CONTENT_SNIPPET_TO_DOCUMENT: Final[str] = "sng_proc__add_content_snippet_to_document"
    ADD_KEYWORD_TO_DOCUMENT: Final[str] = "sng_proc__add_keyword_to_document"
    ADD_LINK_TO_DOCUMENT: Final[str] = "sng_proc__add_link_to_document"
    ADD_IMAGE_TO_DOCUMENT: Final[str] = "sng_proc__add_image_to_document"


# Generated with:
#
#   import os
#   import re
#
#   DB_OBJECTS_DIR = "/home/development/PycharmProjects/spideriment-ng/src/spideriment_ng/modules/databases/mysql/db_objects"
#   DB_OBJECTS_FILENAMES = sorted(os.listdir(DB_OBJECTS_DIR))
#
#   for name, char in (("Procedures", "P"), ("Functions", "F")):
#       routines = map(lambda item: re.match(r'^[0-9]{3}' + char + r'_(.+)\.sql', item), DB_OBJECTS_FILENAMES)
#       routines = filter(None, routines)
#       routines = map(lambda item: item.group(1), routines)
#
#       print(f"--- {name} ---")
#       for routine in routines:
#           var_name = routine.split("__")[1].upper()
#           print(f"{var_name}: Final[str] = \"{routine}\"")
#       print()
