# SPDX-FileCopyrightText: © 2024 Shaun Wilson
# SPDX-License-Identifier: MIT

import os
import src as appsettings2
import unittest

class ConfigurationBuilderTests(unittest.TestCase):

    def test_WithoutProviders_MustSucceed(self):
        builder = appsettings2.ConfigurationBuilder()
        configuration = builder.build()
        self.assertIsNotNone(configuration)

    def test_RequestForNonExistentKey_MustSucceed(self):
        builder = appsettings2.ConfigurationBuilder()
        configuration = builder.build()
        self.assertIsNotNone(configuration)
        v = configuration.get('non_existent_key')
        self.assertIsNone(v)

    def test_WithUninitalizedProviders_MustSucceed(self):
        builder = appsettings2.ConfigurationBuilder()
        builder.addProvider(appsettings2.providers.CommandLineConfigurationProvider([]))
        builder.addProvider(appsettings2.providers.EnvironmentConfigurationProvider())
        builder.addProvider(appsettings2.providers.JsonConfigurationProvider())
        builder.addProvider(appsettings2.providers.TomlConfigurationProvider())
        builder.addProvider(appsettings2.providers.YamlConfigurationProvider())
        configuration = builder.build()
        self.assertIsNotNone(configuration)

    def test_WithSubsetConfigurations_MustLoad(self):
        builder = appsettings2.ConfigurationBuilder()
        builder.addProvider(appsettings2.providers.CommandLineConfigurationProvider([
            'TEST_ARGV=5',
            'some_subobj__TEST_ARGV=6'
        ]))
        os.environ['env_test'] = '7'
        os.environ['some_obj__env_test'] = '8'
        builder.addProvider(appsettings2.providers.EnvironmentConfigurationProvider())
        builder.addProvider(appsettings2.providers.JsonConfigurationProvider(filepath='tests/configs/subset.json'))
        builder.addProvider(appsettings2.providers.TomlConfigurationProvider(filepath='tests/configs/subset.toml'))
        builder.addProvider(appsettings2.providers.YamlConfigurationProvider(filepath='tests/configs/subset.yaml'))
        configuration = builder.build()
        self.assertIsNotNone(configuration)

    def test_WithSubsetConfigurations_MustMatch(self):
        # "subset configurations" are a set of
        # configurations which each configure a subset
        # of the entire config, and are meant to be
        # used to do a broad verification that 
        # all providers work as intended when added
        # to the builder.
        builder = appsettings2.ConfigurationBuilder()
        builder.addProvider(appsettings2.providers.CommandLineConfigurationProvider([
            'TEST_ARGV=5',
            'some_subobj__TEST_ARGV=6'
        ]))
        os.environ['env_test'] = '7'
        os.environ['some_obj__env_test'] = '8'
        builder.addProvider(appsettings2.providers.EnvironmentConfigurationProvider())
        builder.addProvider(appsettings2.providers.JsonConfigurationProvider(filepath='tests/configs/subset.json'))
        builder.addProvider(appsettings2.providers.TomlConfigurationProvider(filepath='tests/configs/subset.toml'))
        builder.addProvider(appsettings2.providers.YamlConfigurationProvider(filepath='tests/configs/subset.yaml'))
        configuration = builder.build()
        self.assertIsNotNone(configuration)
        self.assertEqual(1, configuration.get('some_float'))
        self.assertEqual('rand2', configuration.get('some_subobj:some_string'))
        self.assertEqual(3, configuration.get('some_int'))
        self.assertEqual(3.4, configuration.get('some_subobj:some_float'))
        self.assertEqual('rand4', configuration.get('some_string'))
        self.assertEqual(4, configuration.get('some_subobj:some_int'))
        self.assertEqual('5', configuration.get('TEST_ARGV'))
        self.assertEqual('6', configuration.get('some_subobj__TEST_ARGV'))
        self.assertEqual('7', configuration.get('env_test'))
        self.assertEqual('8', configuration.get('some_obj__env_test'))

    def test_WithExactConfigurations_LastInWins(self):
        # ConfigurationProvider order matters
        #
        # the last provider in the list of providers
        # should be the provider which has the final
        # say over any configuration value.
        #
        # this test confirms that expectation
        #
        # this is a combined function of ConfigurationBuilder
        # and Configuration classes.
        builder = appsettings2.ConfigurationBuilder()
        builder.addProvider(appsettings2.providers.CommandLineConfigurationProvider([
            'TEST_ARGV=5',
            'some_subobj__TEST_ARGV=6'
        ]))
        os.environ['env_test'] = '7'
        os.environ['some_obj__env_test'] = '8'
        builder\
            .addProvider(appsettings2.providers.EnvironmentConfigurationProvider())\
            .addProvider(appsettings2.providers.JsonConfigurationProvider(filepath='tests/configs/exact.json'))
        configuration = builder.build()
        self.assertIsNotNone(configuration)
        self.assertEqual(1, configuration.get('some_int'))
        self.assertEqual(1.1, configuration.get('some_float'))
        self.assertEqual('rand1', configuration.get('some_string'))
        self.assertEqual(1, configuration.get('some_subobj:some_int'))
        self.assertEqual(1.1, configuration.get('some_subobj:some_float'))
        self.assertEqual('rand1', configuration.get('some_subobj:some_string'))
        builder.addProvider(appsettings2.providers.TomlConfigurationProvider(filepath='tests/configs/exact.toml'))
        configuration = builder.build()
        self.assertIsNotNone(configuration)
        self.assertEqual(2, configuration.get('some_int'))
        self.assertEqual(2.2, configuration.get('some_float'))
        self.assertEqual('rand2', configuration.get('some_string'))
        self.assertEqual(2, configuration.get('some_subobj:some_int'))
        self.assertEqual(2.2, configuration.get('some_subobj:some_float'))
        self.assertEqual('rand2', configuration.get('some_subobj:some_string'))
        builder.addProvider(appsettings2.providers.YamlConfigurationProvider(filepath='tests/configs/exact.yaml'))
        configuration = builder.build()
        self.assertIsNotNone(configuration)
        self.assertEqual(3, configuration.get('some_int'))
        self.assertEqual(3.3, configuration.get('some_float'))
        self.assertEqual('rand3', configuration.get('some_string'))
        self.assertEqual(3, configuration.get('some_subobj:some_int'))
        self.assertEqual(3.3, configuration.get('some_subobj:some_float'))
        self.assertEqual('rand3', configuration.get('some_subobj:some_string'))
