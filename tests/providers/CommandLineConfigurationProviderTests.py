# SPDX-FileCopyrightText: © 2024 Shaun Wilson
# SPDX-License-Identifier: MIT

import src as appsettings2
import unittest

class CommandLineConfigurationProviderTests(unittest.TestCase):

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
        self.assertEqual('1', configuration.get('TEST_ARGV'))
        self.assertEqual('2', configuration.get('some_subobj:TEST_ARGV'))
        self.assertTrue(configuration.get('switch1'))
        self.assertEqual('3', configuration.get('switched-arg'))
        self.assertTrue(configuration.get('switch2'))

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
        self.assertEqual('1', configuration.get('TEST_ARGV'))
        self.assertEqual('2', configuration.get('some_subobj:TEST_ARGV'))
        self.assertTrue(configuration.get('switch1'))
        self.assertEqual('3', configuration.get('switched-arg'))
        self.assertTrue(configuration.get('switch2'))
