# SPDX-FileCopyrightText: © 2025 Shaun Wilson
# SPDX-License-Identifier: MIT

import appsettings2
from punit import fact


class TomlConfigurationProviderTests:

    @fact
    def test_BasicVerification(self):
        provider = appsettings2.providers.TomlConfigurationProvider(
            toml="""
toml_test = "1"

[some_subobj]
toml_test = 2
""")
        configuration = appsettings2.Configuration()
        provider.populateConfiguration(configuration)
        assert '1' == configuration.get('toml_test')
        assert 2 == configuration.get('some_subobj:toml_test')
