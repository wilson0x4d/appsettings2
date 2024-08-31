# SPDX-FileCopyrightText: © 2024 Shaun Wilson
# SPDX-License-Identifier: MIT

import os
import src as appsettings2
import unittest

class EnvironmentConfigurationProviderTests(unittest.TestCase):

    def test_BasicVerification(self):
        os.environ['ENV_TEST'] = '1'
        os.environ['some_subobj__ENV_TEST'] = '2'
        provider = appsettings2.providers.EnvironmentConfigurationProvider()
        configuration = appsettings2.Configuration()
        provider.populateConfiguration(configuration)
        self.assertEqual('1', configuration.get('ENV_TEST'))
        self.assertEqual('2', configuration.get('some_subobj:ENV_TEST'))
