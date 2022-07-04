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


from typing import Final, Optional, Sequence, Tuple
import re
import urllib.parse
from spideriment_ng.config.FilterRule import FilterRule
from spideriment_ng.helpers.containers.document.URLContainer import URLContainer
from spideriment_ng.worker.workertask._normalizers._FilterRuleChecker import _FilterRuleChecker
from spideriment_ng.worker.workertask._normalizers.exc.FailedToParseURLExc import FailedToParseURLExc
from spideriment_ng.worker.workertask._normalizers.exc.FailedToAbsolutizeURLExc import FailedToAbsolutizeURLExc
from spideriment_ng.worker.workertask._normalizers.exc.URLBlockedByFilterRuleExc import URLBlockedByFilterRuleExc
from spideriment_ng.worker.workertask._normalizers.exc.ForbiddenURLSchemeExc import ForbiddenURLSchemeExc
from spideriment_ng.worker.workertask._normalizers.exc.ForbiddenPortNumberExc import ForbiddenPortNumberExc
from spideriment_ng.worker.workertask._normalizers.exc.URLContainsCredentialsExc import URLContainsCredentialsExc
from spideriment_ng.worker.workertask._normalizers.exc.InvalidHostnameInURLExc import InvalidHostnameInURLExc
from spideriment_ng.worker.workertask._normalizers.exc.URLEncodingFailureExc import URLEncodingFailureExc
from spideriment_ng.worker.workertask._normalizers.exc.URLTooLongExc import URLTooLongExc


class URLNormalizer:
    _ENCODING: Final[str] = "utf-8"

    def __init__(self, whole_url_filter_rules: Sequence[FilterRule], host_filter_rules: Sequence[FilterRule],
                 path_filter_rules: Sequence[FilterRule], query_filter_rules: Sequence[FilterRule],
                 url_max_length: int, remove_query_parameters_matching_regex: Sequence[re.Pattern],
                 allow_nonstandard_ports: bool):
        assert (url_max_length > 0)

        self._whole_url_filter_rule_checker: Final[_FilterRuleChecker] = _FilterRuleChecker(whole_url_filter_rules)
        self._host_filter_rule_checker: Final[_FilterRuleChecker] = _FilterRuleChecker(host_filter_rules)
        self._path_filter_rule_checker: Final[_FilterRuleChecker] = _FilterRuleChecker(path_filter_rules)
        self._query_filter_rule_checker: Final[_FilterRuleChecker] = _FilterRuleChecker(query_filter_rules)
        self._url_max_length: Final[int] = url_max_length
        self._remove_query_parameters_matching_regex: Final[Tuple[re.Pattern, ...]] = tuple(remove_query_parameters_matching_regex)
        self._allow_nonstandard_ports: Final[bool] = allow_nonstandard_ports

    def use_on_possibly_relative_url(self, validated_absolute_base_url: URLContainer, unvalidated_nonabsolute_url: URLContainer) -> URLContainer:
        """
        :raises NormalizerBaseExc
        """

        assert (validated_absolute_base_url.is_validated() and validated_absolute_base_url.is_certainly_absolute())
        assert (not unvalidated_nonabsolute_url.is_validated()) and (not unvalidated_nonabsolute_url.is_certainly_absolute())

        base_url_string = validated_absolute_base_url.get_url()
        possibly_relative_url_string = unvalidated_nonabsolute_url.get_url()

        try:
            absolute_url_string = urllib.parse.urljoin(
                base=base_url_string,
                url=possibly_relative_url_string,
                allow_fragments=True
            )
        except Exception:
            raise FailedToAbsolutizeURLExc(base_url_string, possibly_relative_url_string)

        return self._use_on_absolute_url_string(absolute_url_string)

    def use_on_absolute_url(self, unvalidated_absolute_url: URLContainer) -> URLContainer:
        """
        :raises NormalizerBaseExc
        """

        assert (not unvalidated_absolute_url.is_validated()) and unvalidated_absolute_url.is_certainly_absolute()

        return self._use_on_absolute_url_string(unvalidated_absolute_url.get_url())

    def _use_on_absolute_url_string(self, initial_url_string: str) -> URLContainer:
        initial_url_string = initial_url_string.strip()

        try:
            initial_split_url = urllib.parse.urlsplit(initial_url_string, allow_fragments=True)
        except Exception:
            raise FailedToParseURLExc(initial_url_string)

        final_split_url = urllib.parse.SplitResult(
            scheme=self._construct_new_scheme(initial_split_url.scheme),
            netloc=self._construct_new_netloc(initial_split_url, initial_url_string),
            path=self._construct_new_path(initial_split_url.path, initial_url_string),
            query=self._construct_new_query(initial_split_url.query, initial_url_string),
            fragment=""
        )  # noqa

        final_url_string = urllib.parse.urlunsplit(final_split_url).strip()

        self._check_url_or_url_part_using_filter_rule_checker(self._whole_url_filter_rule_checker, final_url_string)
        if len(final_url_string) > self._url_max_length:
            raise URLTooLongExc(final_url_string, self._url_max_length)

        return URLContainer(
            validated=True,
            certainly_absolute=True,
            url=final_url_string
        )

    def _construct_new_scheme(self, initial_url_scheme: str) -> str:
        new_url_scheme = initial_url_scheme.strip().lower()

        if new_url_scheme in ("http", "https"):
            return new_url_scheme

        raise ForbiddenURLSchemeExc(new_url_scheme)

    def _construct_new_netloc(self, initial_split_url: urllib.parse.SplitResult, initial_url_string: str) -> str:
        # Username & password
        if (initial_split_url.username is not None) or (initial_split_url.password is not None):
            raise URLContainsCredentialsExc()

        # Hostname
        new_netloc = initial_split_url.hostname
        if new_netloc is None:
            raise InvalidHostnameInURLExc("")

        new_netloc = new_netloc.strip().strip(".").strip().lower()
        if (
            (not re.match(r'^[0-9a-z._-]+\Z', new_netloc)) or
            re.match(r'^[-_]', new_netloc) or
            re.search(r'[-_]\Z', new_netloc) or
            (".." in new_netloc) or
            new_netloc.endswith(".onion")
        ):
            raise InvalidHostnameInURLExc(new_netloc)

        self._check_url_or_url_part_using_filter_rule_checker(self._host_filter_rule_checker, new_netloc)

        # Port
        port_number = self._get_and_check_port_number(initial_split_url, initial_url_string)
        if port_number is not None:
            new_netloc += f":{port_number}"

        return new_netloc

    def _get_and_check_port_number(self, initial_split_url: urllib.parse.SplitResult, initial_url_string: str) -> Optional[int]:
        try:
            port_number = initial_split_url.port
        except Exception:  # Raised when an out-of-range port number is in the URL
            raise ForbiddenPortNumberExc(initial_url_string)

        if port_number is None:
            return None

        scheme = initial_split_url.scheme.strip().lower()
        if (scheme == "http" and port_number == 80) or (scheme == "https" and port_number == 443):
            return None  # Standard port number do not need to be specified explicitly

        if self._allow_nonstandard_ports:
            return port_number
        raise ForbiddenPortNumberExc(initial_url_string)

    def _construct_new_path(self, initial_url_path: str, initial_url_string: str) -> str:
        try:
            new_url_path = urllib.parse.unquote(initial_url_path, encoding=self.__class__._ENCODING, errors="strict")
        except UnicodeError:
            raise URLEncodingFailureExc(initial_url_string, self.__class__._ENCODING)

        new_url_path = re.sub(r'/+', '/', new_url_path).strip()

        if not new_url_path.startswith("/"):
            new_url_path = ("/" + new_url_path)

        try:
            new_url_path = urllib.parse.quote(new_url_path, safe="/", encoding=self.__class__._ENCODING, errors="strict")
        except UnicodeError:
            raise URLEncodingFailureExc(initial_url_string, self.__class__._ENCODING)

        self._check_url_or_url_part_using_filter_rule_checker(self._path_filter_rule_checker, new_url_path)
        return new_url_path

    def _construct_new_query(self, initial_url_query: str, initial_url_string: str) -> str:
        try:
            query_params = urllib.parse.parse_qsl(qs=initial_url_query, keep_blank_values=False, strict_parsing=False,
                                                  encoding=self.__class__._ENCODING, errors="strict",
                                                  max_num_fields=None, separator="&")
        except UnicodeError:
            raise URLEncodingFailureExc(initial_url_string, self.__class__._ENCODING)

        cleaned_query_params = []
        for key, value in query_params:
            key = key.strip()
            if (not key) or self._should_query_param_be_removed(key):
                continue
            cleaned_query_params.append((key, value.strip()))

        try:
            new_url_query = urllib.parse.urlencode(cleaned_query_params, doseq=False, safe="",
                                                   encoding=self.__class__._ENCODING, errors="strict",
                                                   quote_via=urllib.parse.quote_plus)
        except UnicodeError:
            raise URLEncodingFailureExc(initial_url_string, self.__class__._ENCODING)

        self._check_url_or_url_part_using_filter_rule_checker(self._query_filter_rule_checker, new_url_query)
        return new_url_query

    def _should_query_param_be_removed(self, query_param_key: str) -> bool:
        for regex_pattern in self._remove_query_parameters_matching_regex:
            if regex_pattern.search(query_param_key):
                return True
        return False

    def _check_url_or_url_part_using_filter_rule_checker(self, filter_rule_checker: _FilterRuleChecker, url_or_url_part: str) -> None:
        if not filter_rule_checker.check_string(url_or_url_part):
            raise URLBlockedByFilterRuleExc(url_or_url_part)
