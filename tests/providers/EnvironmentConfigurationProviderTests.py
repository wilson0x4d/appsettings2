# SPDX-FileCopyrightText: Copyright (C) Shaun Wilson
# SPDX-License-Identifier: MIT

import os
import appsettings2
from punit import *

class EnvironmentConfigurationProviderTests:

    @fact
    def test_BasicVerification(self):
        os.environ['ENV_TEST'] = '1'
        os.environ['some_subobj__ENV_TEST'] = '2'
        provider = appsettings2.providers.EnvironmentConfigurationProvider()
        configuration = appsettings2.Configuration()
        provider.populateConfiguration(configuration)
        assert '1' == configuration.get('ENV_TEST')
        assert '2' == configuration.get('some_subobj:ENV_TEST')
