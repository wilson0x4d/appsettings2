# SPDX-FileCopyrightText: © 2025 Shaun Wilson
# SPDX-License-Identifier: MIT

import appsettings2
from punit import fact


class JsonConfigurationProviderTests:

    @fact
    def basic_verification_test(self) -> None:
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
