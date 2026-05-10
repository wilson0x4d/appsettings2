# SPDX-FileCopyrightText: © 2025 Shaun Wilson
# SPDX-License-Identifier: MIT

import appsettings2
from punit import fact


class YamlConfigurationProviderTests:

    @fact
    def test_BasicVerification(self) -> None:
        provider = appsettings2.providers.YamlConfigurationProvider(
            yaml="""
yaml_test: "1"
some_subobj:
  yaml_test: 2
""")
        configuration = appsettings2.Configuration()
        provider.populateConfiguration(configuration)
        assert '1' == configuration.get('yaml_test')
        assert 2 == configuration.get('some_subobj:yaml_test')
