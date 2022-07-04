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
from datalidator.blueprints.impl.ObjectBlueprint import ObjectBlueprint
from datalidator.blueprints.impl.DictionaryBlueprint import DictionaryBlueprint
from datalidator.blueprints.impl.IntegerBlueprint import IntegerBlueprint
from datalidator.validators.impl.SequenceIsNotEmptyValidator import SequenceIsNotEmptyValidator
from datalidator.validators.impl.IntegerIsPositiveValidator import IntegerIsPositiveValidator
from spideriment_ng.supervisor.configload._GenericConfigModel import _GenericConfigModel
from spideriment_ng.supervisor.configload._LimitsConfigModel import _LimitsConfigModel
from spideriment_ng.supervisor.configload._FilteringConfigModel import _FilteringConfigModel
from spideriment_ng.supervisor.configload._ModuleConfigModel import _ModuleConfigModel


class _ConfigModel(ObjectModel):
    generic = ObjectBlueprint(_GenericConfigModel)
    limits = ObjectBlueprint(_LimitsConfigModel)
    filtering = ObjectBlueprint(_FilteringConfigModel)
    fetcher = ObjectBlueprint(_ModuleConfigModel)
    database = ObjectBlueprint(_ModuleConfigModel)
    document_parsers = DictionaryBlueprint(
        key_blueprint=IntegerBlueprint(
            validators=(IntegerIsPositiveValidator(),)
        ),
        value_blueprint=ObjectBlueprint(_ModuleConfigModel),
        validators=(SequenceIsNotEmptyValidator(),)
    )
    robot_caches = DictionaryBlueprint(
        key_blueprint=IntegerBlueprint(
            validators=(IntegerIsPositiveValidator(),)
        ),
        value_blueprint=ObjectBlueprint(_ModuleConfigModel)
    )
