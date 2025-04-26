# SPDX-FileCopyrightText: Copyright (C) Shaun Wilson
# SPDX-License-Identifier: MIT

import appsettings2
import os
from punit import *

class ConfigurationBuilderTests:

    @fact
    def test_WithoutProviders_MustSucceed(self):
        builder = appsettings2.ConfigurationBuilder()
        configuration = builder.build()
        assert configuration is not None

    @fact
    def test_RequestForNonExistentKey_MustSucceed(self):
        builder = appsettings2.ConfigurationBuilder()
        configuration = builder.build()
        assert configuration is not None
        v = configuration.get('non_existent_key')
        assert v is None

    @fact
    def test_WithUninitalizedProviders_MustSucceed(self):
        builder = appsettings2.ConfigurationBuilder()
        builder.addProvider(appsettings2.providers.CommandLineConfigurationProvider([]))
        builder.addProvider(appsettings2.providers.EnvironmentConfigurationProvider())
        builder.addProvider(appsettings2.providers.JsonConfigurationProvider())
        builder.addProvider(appsettings2.providers.TomlConfigurationProvider())
        builder.addProvider(appsettings2.providers.YamlConfigurationProvider())
        configuration = builder.build()
        assert configuration is not None

    @fact
    def test_WithSubsetConfigurations_MustLoad(self):
        builder = appsettings2.ConfigurationBuilder()
        builder.addProvider(appsettings2.providers.CommandLineConfigurationProvider([
            'TEST_ARGV=5',
            'some_subobj__TEST_ARGV=6'
        ]))
        os.environ['env_test'] = '7'
        os.environ['some_obj__env_test'] = '8'
        builder.addProvider(appsettings2.providers.EnvironmentConfigurationProvider())
        builder.addProvider(appsettings2.providers.JsonConfigurationProvider('tests/configs/subset.json'))
        builder.addProvider(appsettings2.providers.TomlConfigurationProvider('tests/configs/subset.toml'))
        builder.addProvider(appsettings2.providers.YamlConfigurationProvider('tests/configs/subset.yaml'))
        configuration = builder.build()
        assert configuration is not None

    @fact
    def test_WithSubsetConfigurations_MustMatch(self):
        # "subset configurations" are a set of
        # configurations which each configure a subset
        # of the entire config, and are meant to be
        # used to do a broad verification that 
        # all providers work as intended when added
        # to the builder.
        builder = appsettings2.ConfigurationBuilder()
        builder.addCommandLine([
            'TEST_ARGV=5',
            'some_subobj__TEST_ARGV=6'
        ])
        os.environ['env_test'] = '7'
        os.environ['some_obj__env_test'] = '8'
        builder.addEnvironment()
        builder.addJson('tests/configs/subset.json')
        builder.addToml('tests/configs/subset.toml')
        builder.addYaml('tests/configs/subset.yaml')
        configuration = builder.build()
        assert configuration is not None
        assert 1 == configuration.get('some_float')
        assert 'rand2' == configuration.get('some_subobj:some_string')
        assert 3 == configuration.get('some_int')
        assert 3.4 == configuration.get('some_subobj:some_float')
        assert 'rand4' == configuration.get('some_string')
        assert 4 == configuration.get('some_subobj:some_int')
        assert '5' == configuration.get('TEST_ARGV')
        assert '6' == configuration.get('some_subobj__TEST_ARGV')
        assert '7' == configuration.get('env_test')
        assert '8' == configuration.get('some_obj__env_test')

    @fact
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
        builder.addCommandLine([
            'TEST_ARGV=5',
            'some_subobj__TEST_ARGV=6'
        ])
        os.environ['env_test'] = '7'
        os.environ['some_obj__env_test'] = '8'
        builder\
            .addEnvironment()\
            .addJson('tests/configs/exact.json')
        configuration = builder.build()
        assert configuration is not None
        assert 1 == configuration.get('some_int')
        assert 1.1 == configuration.get('some_float')
        assert 'rand1' == configuration.get('some_string')
        assert 1 == configuration.get('some_subobj:some_int')
        assert 1.1 == configuration.get('some_subobj:some_float')
        assert 'rand1' == configuration.get('some_subobj:some_string')
        builder.addProvider(appsettings2.providers.TomlConfigurationProvider('tests/configs/exact.toml'))
        configuration = builder.build()
        assert configuration is not None
        assert 2 == configuration.get('some_int')
        assert 2.2 == configuration.get('some_float')
        assert 'rand2' == configuration.get('some_string')
        assert 2 == configuration.get('some_subobj:some_int')
        assert 2.2 == configuration.get('some_subobj:some_float')
        assert 'rand2' == configuration.get('some_subobj:some_string')
        builder.addProvider(appsettings2.providers.YamlConfigurationProvider('tests/configs/exact.yaml'))
        configuration = builder.build()
        assert configuration is not None
        assert 3 == configuration.get('some_int')
        assert 3.3 == configuration.get('some_float')
        assert 'rand3' == configuration.get('some_string')
        assert 3 == configuration.get('some_subobj:some_int')
        assert 3.3 == configuration.get('some_subobj:some_float')
        assert 'rand3' == configuration.get('some_subobj:some_string')

    @fact
    def getConfigurationBasicVerification(self) -> None:
        configuration = appsettings2.getConfiguration('tests/configs/exact', toml=False, yaml=False)
        assert configuration is not None
        assert 1 == configuration.get('some_int')
        assert 1.1 == configuration.get('some_float')
        assert 'rand1' == configuration.get('some_string')
        assert 1 == configuration.get('some_subobj:some_int')
        assert 1.1 == configuration.get('some_subobj:some_float')
        assert 'rand1' == configuration.get('some_subobj:some_string')
        configuration = appsettings2.getConfiguration('tests/configs/exact', json=False, yaml=False)
        assert configuration is not None
        assert 2 == configuration.get('some_int')
        assert 2.2 == configuration.get('some_float')
        assert 'rand2' == configuration.get('some_string')
        assert 2 == configuration.get('some_subobj:some_int')
        assert 2.2 == configuration.get('some_subobj:some_float')
        assert 'rand2' == configuration.get('some_subobj:some_string')
        configuration = appsettings2.getConfiguration('tests/configs/exact', json=False, toml=False)
        assert configuration is not None
        assert 3 == configuration.get('some_int')
        assert 3.3 == configuration.get('some_float')
        assert 'rand3' == configuration.get('some_string')
        assert 3 == configuration.get('some_subobj:some_int')
        assert 3.3 == configuration.get('some_subobj:some_float')
        assert 'rand3' == configuration.get('some_subobj:some_string')
