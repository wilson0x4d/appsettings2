# SPDX-FileCopyrightText: © 2024 Shaun Wilson
# SPDX-License-Identifier: MIT

import src as appsettings2
import unittest

class TomlConfigurationProviderTests(unittest.TestCase):

    def test_BasicVerification(self):
        provider = appsettings2.providers.TomlConfigurationProvider(
            toml="""
toml_test = "1"

[some_subobj]
toml_test = 2
""")
        configuration = appsettings2.Configuration()
        provider.populateConfiguration(configuration)
        self.assertEqual('1', configuration.get('toml_test'))
        self.assertEqual(2, configuration.get('some_subobj:toml_test'))
