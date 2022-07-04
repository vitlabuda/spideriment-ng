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
from datalidator.blueprints.impl.StringBlueprint import StringBlueprint
from datalidator.blueprints.impl.IntegerBlueprint import IntegerBlueprint
from datalidator.filters.impl.StringStripFilter import StringStripFilter
from datalidator.filters.impl.StringLowercaseFilter import StringLowercaseFilter
from datalidator.validators.impl.SequenceIsNotEmptyValidator import SequenceIsNotEmptyValidator
from datalidator.validators.impl.StringMatchesRegexValidator import StringMatchesRegexValidator
from datalidator.validators.impl.NumberMinimumValueValidator import NumberMinimumValueValidator
from datalidator.validators.impl.NumberMaximumValueValidator import NumberMaximumValueValidator


class _MySQLDatabaseModuleConfigModel(ObjectModel):
    mysql_host = StringBlueprint(
        filters=(StringStripFilter(), StringLowercaseFilter()),
        validators=(StringMatchesRegexValidator(r'^[0-9a-z.:%_-]+\Z'),)
    )
    mysql_port = IntegerBlueprint(
        validators=(NumberMinimumValueValidator(1), NumberMaximumValueValidator(65535))
    )
    mysql_user = StringBlueprint(
        filters=(StringStripFilter(),),
        validators=(SequenceIsNotEmptyValidator(),)
    )
    mysql_password = StringBlueprint(
        filters=(StringStripFilter(),),
        validators=(SequenceIsNotEmptyValidator(),)
    )
    mysql_db = StringBlueprint(
        filters=(StringStripFilter(),),
        validators=(SequenceIsNotEmptyValidator(),)
    )
    connection_pool_size = IntegerBlueprint(
        validators=(NumberMinimumValueValidator(1),)
    )
