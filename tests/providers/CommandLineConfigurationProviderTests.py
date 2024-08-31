# SPDX-FileCopyrightText: © 2024 Shaun Wilson
# SPDX-License-Identifier: MIT

import src as appsettings2
import unittest

class CommandLineConfigurationProviderTests(unittest.TestCase):

    def test_BasicVerification(self):
        provider = appsettings2.providers.CommandLineConfigurationProvider([
            'TEST_ARGV=1',
            'some_subobj__TEST_ARGV=2',
        ])
        configuration = appsettings2.Configuration()
        provider.populateConfiguration(configuration)
        self.assertEqual('1', configuration.get('TEST_ARGV'))
        self.assertEqual('2', configuration.get('some_subobj:TEST_ARGV'))
