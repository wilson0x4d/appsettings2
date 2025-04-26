# SPDX-FileCopyrightText: © 2024 Shaun Wilson
# SPDX-License-Identifier: MIT

import appsettings2
from punit import *

class CommandLineConfigurationProviderTests:

    @fact
    def test_BasicVerification1(self):
        provider = appsettings2.providers.CommandLineConfigurationProvider([
            '--switch1',
            'TEST_ARGV=1',
            '--switch2',
            'some_subobj__TEST_ARGV=2',
            '--switched-arg', '3'
        ])
        configuration = appsettings2.Configuration()
        provider.populateConfiguration(configuration)
        assert '1' == configuration.get('TEST_ARGV')
        assert '2' == configuration.get('some_subobj:TEST_ARGV')
        assert True == (configuration.get('switch1'))
        assert '3' == configuration.get('switched-arg')
        assert True == (configuration.get('switch2'))

    @fact
    def test_BasicVerification2(self):
        provider = appsettings2.providers.CommandLineConfigurationProvider([
            'TEST_ARGV=1',
            'some_subobj__TEST_ARGV=2',
            '--switch1',
            '--switched-arg', '3',
            '--switch2'
        ])
        configuration = appsettings2.Configuration()
        provider.populateConfiguration(configuration)
        assert '1' == configuration.get('TEST_ARGV')
        assert '2' == configuration.get('some_subobj:TEST_ARGV')
        assert True == (configuration.get('switch1'))
        assert '3' == configuration.get('switched-arg')
        assert True == (configuration.get('switch2'))
