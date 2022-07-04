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


from typing import Type, Dict, Sequence
import os
import re
import fcntl
import tomlkit
import tomlkit.exceptions
from datalidator.exc.DatalidatorExc import DatalidatorExc
from datalidator.blueprints.impl.ObjectBlueprint import ObjectBlueprint
from spideriment_ng.config.Configuration import Configuration
from spideriment_ng.config.GenericConfiguration import GenericConfiguration
from spideriment_ng.config.LimitsConfiguration import LimitsConfiguration
from spideriment_ng.config.FilteringConfiguration import FilteringConfiguration
from spideriment_ng.config.ConfiguredModule import ConfiguredModule
from spideriment_ng.config.FilterRule import FilterRule
from spideriment_ng.config.FilterRuleType import FilterRuleType
from spideriment_ng.supervisor.configload.exc.FailedToReadConfigFileExc import FailedToReadConfigFileExc
from spideriment_ng.supervisor.configload.exc.FailedToParseConfigExc import FailedToParseConfigExc
from spideriment_ng.supervisor.configload.exc.InvalidConfigContentsExc import InvalidConfigContentsExc
from spideriment_ng.supervisor.configload._ConfigModel import _ConfigModel
from spideriment_ng.supervisor.configload._GenericConfigModel import _GenericConfigModel
from spideriment_ng.supervisor.configload._LimitsConfigModel import _LimitsConfigModel
from spideriment_ng.supervisor.configload._FilteringConfigModel import _FilteringConfigModel
from spideriment_ng.supervisor.configload._ModuleConfigModel import _ModuleConfigModel
from spideriment_ng.modules.ModuleType import ModuleType
from spideriment_ng.modules.ModuleRegistryIface import ModuleRegistryIface
from spideriment_ng.modules.fetchers.FetcherModuleRegistry import FetcherModuleRegistry
from spideriment_ng.modules.databases.DatabaseModuleRegistry import DatabaseModuleRegistry
from spideriment_ng.modules.documentparsers.DocumentParserModuleRegistry import DocumentParserModuleRegistry
from spideriment_ng.modules.robotcaches.RobotCacheModuleRegistry import RobotCacheModuleRegistry


class ConfigurationLoader:
    def load_configuration_from_toml_file(self, toml_file_path: str) -> Configuration:
        try:
            with open(toml_file_path, "r") as toml_file:
                fcntl.flock(toml_file.fileno(), fcntl.LOCK_SH)
                try:
                    toml_string = toml_file.read()
                finally:
                    fcntl.flock(toml_file.fileno(), fcntl.LOCK_UN)
        except OSError as e:
            raise FailedToReadConfigFileExc(toml_file_path, os.getcwd(), str(e))

        return self.load_configuration_from_toml_string(toml_string)

    def load_configuration_from_toml_string(self, toml_string: str) -> Configuration:
        try:
            parsed_config = tomlkit.loads(toml_string)
        except tomlkit.exceptions.TOMLKitError as e:
            raise FailedToParseConfigExc(str(e))

        return self.load_configuration_from_dict(dict(parsed_config))

    def load_configuration_from_dict(self, config_dict: dict) -> Configuration:
        try:
            config_model = ObjectBlueprint(_ConfigModel).use(config_dict)
        except DatalidatorExc as e:
            raise InvalidConfigContentsExc(str(e))

        return self._load_configuration_from_model(config_model)  # noqa

    def _load_configuration_from_model(self, config_model: _ConfigModel) -> Configuration:
        # This does not look good, but the advantage of this approach (instead of, for example, using a for loop + kwargs) is that if an error was there (e.g. bad data type or missing argument), linters would be able to detect it.
        return Configuration(
            generic_configuration=self._load_generic_configuration_from_model(config_model.generic),
            limits_configuration=self._load_limits_configuration_from_model(config_model.limits),
            filtering_configuration=self._load_filtering_configuration_from_model(config_model.filtering),
            fetcher_module=self._load_module_from_model(config_model.fetcher, FetcherModuleRegistry, ModuleType.FETCHER),
            database_module=self._load_module_from_model(config_model.database, DatabaseModuleRegistry, ModuleType.DATABASE),
            ordered_document_parser_modules=self._load_ordered_module_sequence_from_dictionary_with_priorities(config_model.document_parsers, DocumentParserModuleRegistry, ModuleType.DOCUMENT_PARSER),
            ordered_robot_cache_modules=self._load_ordered_module_sequence_from_dictionary_with_priorities(config_model.robot_caches, RobotCacheModuleRegistry, ModuleType.ROBOT_CACHE)
        )

    def _load_generic_configuration_from_model(self, generic_config_model: _GenericConfigModel) -> GenericConfiguration:
        # This does not look good, but the advantage of this approach (instead of, for example, using a for loop + kwargs) is that if an error was there (e.g. bad data type or missing argument), linters would be able to detect it.
        return GenericConfiguration(
            instance_name=generic_config_model.instance_name,
            print_debug_log_messages=generic_config_model.print_debug_log_messages,
            force_garbage_collection=generic_config_model.force_garbage_collection,
            start_urls=generic_config_model.start_urls
        )

    def _load_limits_configuration_from_model(self, limits_config_model: _LimitsConfigModel) -> LimitsConfiguration:
        # This does not look good, but the advantage of this approach (instead of, for example, using a for loop + kwargs) is that if an error was there (e.g. bad data type or missing argument), linters would be able to detect it.
        return LimitsConfiguration(
            worker_processes=limits_config_model.worker_processes,
            worker_tasks_per_process=limits_config_model.worker_tasks_per_process,
            max_document_size=limits_config_model.max_document_size,
            max_robots_txt_size=limits_config_model.max_robots_txt_size,
            request_timeout=limits_config_model.request_timeout,
            url_max_length=limits_config_model.url_max_length,
            max_redirects=limits_config_model.max_redirects,
            max_crawling_delay=limits_config_model.max_crawling_delay,
            title_max_length=limits_config_model.title_max_length,
            description_max_length=limits_config_model.description_max_length,
            keyword_max_length=limits_config_model.keyword_max_length,
            author_max_length=limits_config_model.author_max_length,
            content_snippet_max_length=limits_config_model.content_snippet_max_length,
            link_text_max_length=limits_config_model.link_text_max_length,
            img_alt_text_max_length=limits_config_model.img_alt_text_max_length,
            img_title_max_length=limits_config_model.img_title_max_length,
            max_keywords_per_document=limits_config_model.max_keywords_per_document,
            max_content_snippets_per_document=limits_config_model.max_content_snippets_per_document,
            max_content_snippets_per_type_per_document=limits_config_model.max_content_snippets_per_type_per_document,
            max_links_per_document=limits_config_model.max_links_per_document,
            max_images_per_document=limits_config_model.max_images_per_document
        )

    def _load_filtering_configuration_from_model(self, filtering_config_model: _FilteringConfigModel) -> FilteringConfiguration:
        # This does not look good, but the advantage of this approach (instead of, for example, using a for loop + kwargs) is that if an error was there (e.g. bad data type or missing argument), linters would be able to detect it.
        return FilteringConfiguration(
            url_filters=self._load_filter_rules_from_list(filtering_config_model.url_filters),
            url_host_filters=self._load_filter_rules_from_list(filtering_config_model.url_host_filters),
            url_path_filters=self._load_filter_rules_from_list(filtering_config_model.url_path_filters),
            url_query_filters=self._load_filter_rules_from_list(filtering_config_model.url_query_filters),
            title_filters=self._load_filter_rules_from_list(filtering_config_model.title_filters),
            description_filters=self._load_filter_rules_from_list(filtering_config_model.description_filters),
            keyword_filters=self._load_filter_rules_from_list(filtering_config_model.keyword_filters),
            language_filters=self._load_filter_rules_from_list(filtering_config_model.language_filters),
            author_filters=self._load_filter_rules_from_list(filtering_config_model.author_filters),
            content_snippet_filters=self._load_filter_rules_from_list(filtering_config_model.content_snippet_filters),
            link_text_filters=self._load_filter_rules_from_list(filtering_config_model.link_text_filters),
            img_url_filters=self._load_filter_rules_from_list(filtering_config_model.img_url_filters),
            img_url_host_filters=self._load_filter_rules_from_list(filtering_config_model.img_url_host_filters),
            img_url_path_filters=self._load_filter_rules_from_list(filtering_config_model.img_url_path_filters),
            img_url_query_filters=self._load_filter_rules_from_list(filtering_config_model.img_url_query_filters),
            img_alt_text_filters=self._load_filter_rules_from_list(filtering_config_model.img_alt_text_filters),
            img_title_filters=self._load_filter_rules_from_list(filtering_config_model.img_title_filters),
            remove_query_parameters_matching_regex=self._load_regex_patterns_from_list(filtering_config_model.remove_query_parameters_matching_regex),
            allow_nonstandard_ports=filtering_config_model.allow_nonstandard_ports
        )

    def _load_filter_rules_from_list(self, filter_rule_list: Sequence[Sequence[str]]) -> Sequence[FilterRule]:
        filter_rule_objects = []
        for filter_rule in filter_rule_list:
            rule_type_string, rule_regex_string = tuple(filter_rule)  # A 2-item sequence is guaranteed by the config model

            try:
                rule_type = ({
                    "allow": FilterRuleType.ALLOW,
                    "block": FilterRuleType.BLOCK
                }[rule_type_string.strip().lower()])
            except KeyError:
                raise InvalidConfigContentsExc(f"Filter rule type {repr(rule_type_string)} is not valid!")

            rule_regex = self._compile_regex_from_string(rule_regex_string)

            filter_rule_objects.append(FilterRule(rule_type=rule_type, rule_regex=rule_regex))

        return filter_rule_objects

    def _load_regex_patterns_from_list(self, regex_pattern_string_list: Sequence[str]) -> Sequence[re.Pattern]:
        return [self._compile_regex_from_string(regex_pattern_string) for regex_pattern_string in regex_pattern_string_list]

    def _load_module_from_model(self, module_config_model: _ModuleConfigModel, module_registry: Type[ModuleRegistryIface], module_type: ModuleType) -> ConfiguredModule:
        module_class = module_registry.get_module_by_name(module_config_model.module_name)
        module_info = module_class.get_module_info()

        assert (module_info.get_type() == module_type)

        module_configuration_blueprint = module_info.get_configuration_blueprint()
        if module_configuration_blueprint is None:
            module_options = None
        else:
            try:
                module_options = module_configuration_blueprint.use(module_config_model.module_options)
            except DatalidatorExc as e:
                raise InvalidConfigContentsExc(str(e))

        return ConfiguredModule(module_class=module_class, module_options=module_options)

    def _load_ordered_module_sequence_from_dictionary_with_priorities(self, model_dictionary_with_priorities: Dict[int, _ModuleConfigModel], module_registry: Type[ModuleRegistryIface], module_type: ModuleType) -> Sequence[ConfiguredModule]:
        # Since dictionaries are not mandated to be ordered in Python and module sequences need to be ordered, each
        #  module has a configured priority according to which (in descending order) the modules are sorted after
        #  the dictionary is converted to an ordered sequence.

        module_sequence = [(module_priority, self._load_module_from_model(module_config_model, module_registry, module_type)) for module_priority, module_config_model in model_dictionary_with_priorities.items()]
        module_sequence.sort(key=lambda prio_module: prio_module[0], reverse=True)

        return [prio_module[1] for prio_module in module_sequence]

    def _compile_regex_from_string(self, regex_string: str) -> re.Pattern:
        try:
            return re.compile(pattern=regex_string, flags=re.IGNORECASE)
        except re.error as e:
            raise InvalidConfigContentsExc(f"Invalid regex pattern {repr(regex_string)}: {str(e)}")
