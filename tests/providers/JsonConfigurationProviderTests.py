# SPDX-FileCopyrightText: © 2024 Shaun Wilson
# SPDX-License-Identifier: MIT

import appsettings2
from punit import *

class JsonConfigurationProviderTests:

    @fact
    def test_BasicVerification(self):
        provider = appsettings2.providers.JsonConfigurationProvider(
            json="""
            {
                "json_test": "1",
                "some_subobj": {
                    "json_test": 2
                }
            }""")
        configuration = appsettings2.Configuration()
        provider.populateConfiguration(configuration)
        assert '1' == configuration.get('json_test')
        assert 2 == configuration.get('some_subobj:json_test')
