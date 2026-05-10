# SPDX-FileCopyrightText: © 2025 Shaun Wilson
# SPDX-License-Identifier: MIT

import appsettings2
import os
from punit import fact


class EnvironmentConfigurationProviderTests:

    @fact
    def test_BasicVerification(self) -> None:
        os.environ['ENV_TEST'] = '1'
        os.environ['some_subobj__ENV_TEST'] = '2'
        provider = appsettings2.providers.EnvironmentConfigurationProvider()
        configuration = appsettings2.Configuration()
        provider.populateConfiguration(configuration)
        assert '1' == configuration.get('ENV_TEST')
        assert '2' == configuration.get('some_subobj:ENV_TEST')
