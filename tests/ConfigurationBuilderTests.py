# SPDX-FileCopyrightText: © 2025 Shaun Wilson
# SPDX-License-Identifier: MIT

import appsettings2
import os
import pathlib
from punit import fact


class ConfigurationBuilderTests:

    @fact
    def when_no_args_then_build_default(self) -> None:
        builder = appsettings2.ConfigurationBuilder()
        configuration = builder.build()
        assert configuration is not None

    @fact
    def when_key_not_found_then_return_default(self) -> None:
        builder = appsettings2.ConfigurationBuilder()
        configuration = builder.build()
        assert configuration is not None
        v = configuration.get('non_existent_key')
        assert v is None

    @fact
    def when_provders_uninitialized_then_build_default(self) -> None:
        builder = appsettings2.ConfigurationBuilder()
        builder.add_provider(
            appsettings2.providers.CommandLineConfigurationProvider([]))
        builder.add_provider(
            appsettings2.providers.EnvironmentConfigurationProvider())
        builder.add_provider(appsettings2.providers.JsonConfigurationProvider())
        builder.add_provider(appsettings2.providers.TomlConfigurationProvider())
        builder.add_provider(appsettings2.providers.YamlConfigurationProvider())
        configuration = builder.build()
        assert configuration is not None

    @fact
    def when_subconfig_then_populate(self) -> None:
        builder = appsettings2.ConfigurationBuilder()
        builder.add_provider(appsettings2.providers.CommandLineConfigurationProvider([
            'TEST_ARGV=5',
            'some_subobj__TEST_ARGV=6'
        ]))
        os.environ['env_test'] = '7'
        os.environ['some_obj__env_test'] = '8'
        builder.add_provider(
            appsettings2.providers.EnvironmentConfigurationProvider())
        builder.add_provider(appsettings2.providers.JsonConfigurationProvider(
            'tests/configs/subset.json'))
        builder.add_provider(appsettings2.providers.TomlConfigurationProvider(
            'tests/configs/subset.toml'))
        builder.add_provider(appsettings2.providers.YamlConfigurationProvider(
            'tests/configs/subset.yaml'))
        configuration = builder.build()
        assert configuration is not None

    @fact
    def when_subconfig_then_match(self) -> None:
        # "subset configurations" are a set of
        # configurations which each configure a subset
        # of the entire config, and are meant to be
        # used to do a broad verification that
        # all providers work as intended when added
        # to the builder.
        builder = appsettings2.ConfigurationBuilder()
        builder.add_command_line([
            'TEST_ARGV=5',
            'some_subobj__TEST_ARGV=6'
        ])
        os.environ['env_test'] = '7'
        os.environ['some_obj__env_test'] = '8'
        builder.add_environment()
        builder.add_json('tests/configs/subset.json')
        builder.add_toml('tests/configs/subset.toml')
        builder.add_yaml('tests/configs/subset.yaml')
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
    def when_same_configuration_then_last_in_wins(self) -> None:
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
        builder.add_command_line([
            'TEST_ARGV=5',
            'some_subobj__TEST_ARGV=6'
        ])
        os.environ['env_test'] = '7'
        os.environ['some_obj__env_test'] = '8'
        builder\
            .add_environment()\
            .add_json('tests/configs/exact.json')
        configuration = builder.build()
        assert configuration is not None
        assert 1 == configuration.get('some_int')
        assert 1.1 == configuration.get('some_float')
        assert 'rand1' == configuration.get('some_string')
        assert 1 == configuration.get('some_subobj:some_int')
        assert 1.1 == configuration.get('some_subobj:some_float')
        assert 'rand1' == configuration.get('some_subobj:some_string')
        builder.add_provider(appsettings2.providers.TomlConfigurationProvider(
            'tests/configs/exact.toml'))
        configuration = builder.build()
        assert configuration is not None
        assert 2 == configuration.get('some_int')
        assert 2.2 == configuration.get('some_float')
        assert 'rand2' == configuration.get('some_string')
        assert 2 == configuration.get('some_subobj:some_int')
        assert 2.2 == configuration.get('some_subobj:some_float')
        assert 'rand2' == configuration.get('some_subobj:some_string')
        builder.add_provider(appsettings2.providers.YamlConfigurationProvider(
            'tests/configs/exact.yaml'))
        configuration = builder.build()
        assert configuration is not None
        assert 3 == configuration.get('some_int')
        assert 3.3 == configuration.get('some_float')
        assert 'rand3' == configuration.get('some_string')
        assert 3 == configuration.get('some_subobj:some_int')
        assert 3.3 == configuration.get('some_subobj:some_float')
        assert 'rand3' == configuration.get('some_subobj:some_string')

    @fact
    def get_configuration_bvt(self) -> None:
        configuration = appsettings2.get_configuration(
            'tests/configs/exact', toml=False, yaml=False)
        assert configuration is not None
        assert 1 == configuration.get('some_int')
        assert 1.1 == configuration.get('some_float')
        assert 'rand1' == configuration.get('some_string')
        assert 1 == configuration.get('some_subobj:some_int')
        assert 1.1 == configuration.get('some_subobj:some_float')
        assert 'rand1' == configuration.get('some_subobj:some_string')
        configuration = appsettings2.get_configuration(
            'tests/configs/exact', json=False, yaml=False)
        assert configuration is not None
        assert 2 == configuration.get('some_int')
        assert 2.2 == configuration.get('some_float')
        assert 'rand2' == configuration.get('some_string')
        assert 2 == configuration.get('some_subobj:some_int')
        assert 2.2 == configuration.get('some_subobj:some_float')
        assert 'rand2' == configuration.get('some_subobj:some_string')
        configuration = appsettings2.get_configuration(
            'tests/configs/exact', json=False, toml=False)
        assert configuration is not None
        assert 3 == configuration.get('some_int')
        assert 3.3 == configuration.get('some_float')
        assert 'rand3' == configuration.get('some_string')
        assert 3 == configuration.get('some_subobj:some_int')
        assert 3.3 == configuration.get('some_subobj:some_float')
        assert 'rand3' == configuration.get('some_subobj:some_string')

    @fact
    def get_configuration_supports_pathlib(self) -> None:
        posix_path = pathlib.Path('tests') / 'configs' / 'exact'
        configuration = appsettings2.get_configuration(posix_path, toml=False, yaml=False)
        assert configuration is not None
        assert 1 == configuration.get('some_int')
        assert 1.1 == configuration.get('some_float')
        assert 'rand1' == configuration.get('some_string')
        assert 1 == configuration.get('some_subobj:some_int')
        assert 1.1 == configuration.get('some_subobj:some_float')
        assert 'rand1' == configuration.get('some_subobj:some_string')
