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
from spideriment_ng.config.FilterRule import FilterRule
from spideriment_ng.config.FilterRuleType import FilterRuleType
from spideriment_ng.exc.ThisShouldNeverHappenError import ThisShouldNeverHappenError


class _FilterRuleChecker:
    def __init__(self, filter_rules: Sequence[FilterRule]):
        self._filter_rules: Final[Tuple[FilterRule, ...]] = tuple(filter_rules)

    def check_string(self, checked_string: str) -> bool:
        for filter_rule in self._filter_rules:
            if filter_rule.get_rule_regex().search(checked_string):
                rule_type = filter_rule.get_rule_type()

                if rule_type == FilterRuleType.ALLOW:
                    return True  # If a matching 'ALLOW' rule is encountered, True is returned = the string passed the check

                if rule_type == FilterRuleType.BLOCK:
                    return False  # If a matching 'BLOCK' rule is encountered, False is returned = the string did not pass the check

                raise ThisShouldNeverHappenError(f"An invalid value of the {repr(FilterRuleType.__name__)} enum was encountered: {repr(rule_type)}")

        return True  # If no matching rule is encountered, True is returned = the string passed the check
