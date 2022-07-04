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


from spideriment_ng.config.Configuration import Configuration
from spideriment_ng.worker.di import WORKER_DI_NS
from spideriment_ng.worker.workertask._normalizers.TextNormalizer import TextNormalizer
from spideriment_ng.worker.workertask._normalizers.URLNormalizer import URLNormalizer
from spideriment_ng.worker.workertask._normalizers.DocumentNormalizer import DocumentNormalizer


class NormalizerFactory:  # DP: Factory
    @WORKER_DI_NS.inject_dependencies("configuration")
    def generate_url_normalizer_using_program_config(self, configuration: Configuration) -> URLNormalizer:
        filtering_config = configuration.get_filtering_configuration()
        limits_config = configuration.get_limits_configuration()

        return URLNormalizer(
            whole_url_filter_rules=filtering_config.get_url_filters(),
            host_filter_rules=filtering_config.get_url_host_filters(),
            path_filter_rules=filtering_config.get_url_path_filters(),
            query_filter_rules=filtering_config.get_url_query_filters(),
            url_max_length=limits_config.get_url_max_length(),
            remove_query_parameters_matching_regex=filtering_config.get_remove_query_parameters_matching_regex(),
            allow_nonstandard_ports=filtering_config.get_allow_nonstandard_ports()
        )

    @WORKER_DI_NS.inject_dependencies("configuration")
    def generate_document_normalizer_using_program_config(self, configuration: Configuration) -> DocumentNormalizer:
        filtering_config = configuration.get_filtering_configuration()
        limits_config = configuration.get_limits_configuration()

        return DocumentNormalizer(
            title_normalizer=TextNormalizer(
                filter_rules=filtering_config.get_title_filters(),
                max_length=limits_config.get_title_max_length()
            ),
            description_normalizer=TextNormalizer(
                filter_rules=filtering_config.get_description_filters(),
                max_length=limits_config.get_description_max_length()
            ),
            keyword_normalizer=TextNormalizer(
                filter_rules=filtering_config.get_keyword_filters(),
                max_length=limits_config.get_keyword_max_length()
            ),
            max_keywords=limits_config.get_max_keywords_per_document(),
            language_filter_rules=filtering_config.get_language_filters(),
            author_normalizer=TextNormalizer(
                filter_rules=filtering_config.get_author_filters(),
                max_length=limits_config.get_author_max_length()
            ),
            content_snippet_normalizer=TextNormalizer(
                filter_rules=filtering_config.get_content_snippet_filters(),
                max_length=limits_config.get_content_snippet_max_length()
            ),
            max_content_snippets=limits_config.get_max_content_snippets_per_document(),
            max_content_snippets_per_type=limits_config.get_max_content_snippets_per_type_per_document(),
            link_href_url_normalizer=self.generate_url_normalizer_using_program_config(),
            link_text_normalizer=TextNormalizer(
                filter_rules=filtering_config.get_link_text_filters(),
                max_length=limits_config.get_link_text_max_length()
            ),
            max_links=limits_config.get_max_links_per_document(),
            image_src_url_normalizer=URLNormalizer(
                whole_url_filter_rules=filtering_config.get_img_url_filters(),
                host_filter_rules=filtering_config.get_img_url_host_filters(),
                path_filter_rules=filtering_config.get_img_url_path_filters(),
                query_filter_rules=filtering_config.get_img_url_query_filters(),
                url_max_length=limits_config.get_url_max_length(),
                remove_query_parameters_matching_regex=filtering_config.get_remove_query_parameters_matching_regex(),
                allow_nonstandard_ports=filtering_config.get_allow_nonstandard_ports()
            ),
            image_alt_text_normalizer=TextNormalizer(
                filter_rules=filtering_config.get_img_alt_text_filters(),
                max_length=limits_config.get_img_alt_text_max_length()
            ),
            image_title_text_normalizer=TextNormalizer(
                filter_rules=filtering_config.get_img_title_filters(),
                max_length=limits_config.get_img_title_max_length()
            ),
            max_images=limits_config.get_max_images_per_document()
        )
