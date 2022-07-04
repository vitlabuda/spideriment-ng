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


from datalidator.blueprints.extras.ObjectModel import ObjectModel
from datalidator.blueprints.impl.ListBlueprint import ListBlueprint
from datalidator.blueprints.impl.StringBlueprint import StringBlueprint
from datalidator.blueprints.impl.BooleanBlueprint import BooleanBlueprint
from datalidator.validators.impl.SequenceMinimumLengthValidator import SequenceMinimumLengthValidator
from datalidator.validators.impl.SequenceMaximumLengthValidator import SequenceMaximumLengthValidator


_FILTER_RULE_LIST_BLUEPRINT = ListBlueprint(
    item_blueprint=ListBlueprint(
        item_blueprint=StringBlueprint(),
        validators=(SequenceMinimumLengthValidator(2), SequenceMaximumLengthValidator(2))
    )
)


class _FilteringConfigModel(ObjectModel):
    url_filters = _FILTER_RULE_LIST_BLUEPRINT
    url_host_filters = _FILTER_RULE_LIST_BLUEPRINT
    url_path_filters = _FILTER_RULE_LIST_BLUEPRINT
    url_query_filters = _FILTER_RULE_LIST_BLUEPRINT
    title_filters = _FILTER_RULE_LIST_BLUEPRINT
    description_filters = _FILTER_RULE_LIST_BLUEPRINT
    keyword_filters = _FILTER_RULE_LIST_BLUEPRINT
    language_filters = _FILTER_RULE_LIST_BLUEPRINT
    author_filters = _FILTER_RULE_LIST_BLUEPRINT
    content_snippet_filters = _FILTER_RULE_LIST_BLUEPRINT
    link_text_filters = _FILTER_RULE_LIST_BLUEPRINT
    img_url_filters = _FILTER_RULE_LIST_BLUEPRINT
    img_url_host_filters = _FILTER_RULE_LIST_BLUEPRINT
    img_url_path_filters = _FILTER_RULE_LIST_BLUEPRINT
    img_url_query_filters = _FILTER_RULE_LIST_BLUEPRINT
    img_alt_text_filters = _FILTER_RULE_LIST_BLUEPRINT
    img_title_filters = _FILTER_RULE_LIST_BLUEPRINT
    remove_query_parameters_matching_regex = ListBlueprint(
        item_blueprint=StringBlueprint()
    )
    allow_nonstandard_ports = BooleanBlueprint()
