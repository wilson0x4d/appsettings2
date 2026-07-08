# SPDX-FileCopyrightText: © 2025 Shaun Wilson
# SPDX-License-Identifier: MIT

import appsettings2
import os
import pathlib
from punit import fact


@fact
def when_no_args_then_build_default() -> None:
    builder = appsettings2.ConfigurationBuilder()
    configuration = builder.build()
    assert configuration is not None


@fact
def when_key_not_found_then_return_default() -> None:
    builder = appsettings2.ConfigurationBuilder()
    configuration = builder.build()
    assert configuration is not None
    v = configuration.get('non_existent_key')
    assert v is None


@fact
def when_provders_uninitialized_then_build_default() -> None:
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
def when_subconfig_then_populate() -> None:
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
def when_subconfig_then_match() -> None:
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
def when_same_configuration_then_last_in_wins() -> None:
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
def get_configuration_bvt() -> None:
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
def get_configuration_supports_pathlib() -> None:
    posix_path = pathlib.Path('tests') / 'configs' / 'exact'
    configuration = appsettings2.get_configuration(posix_path, toml=False, yaml=False)
    assert configuration is not None
    assert 1 == configuration.get('some_int')
    assert 1.1 == configuration.get('some_float')
    assert 'rand1' == configuration.get('some_string')
    assert 1 == configuration.get('some_subobj:some_int')
    assert 1.1 == configuration.get('some_subobj:some_float')
    assert 'rand1' == configuration.get('some_subobj:some_string')


@fact
def when_add_environment_with_required_prefix_then_filters_env_vars() -> None:
    """Ensure add_environment(required_prefix=...) filters env vars to only those starting with the prefix."""
    os.environ['PREFIX_DATABASE_HOST'] = 'db.example.com'
    os.environ['DATABASE_HOST'] = 'other.example.com'  # should be filtered out
    builder = appsettings2.ConfigurationBuilder()
    builder.add_environment(required_prefix='PREFIX_')
    configuration = builder.build()
    assert configuration is not None
    assert 'db.example.com' == configuration.get('DATABASE_HOST')
    assert configuration.get('OTHER:DATABASE_HOST') is None


@fact
def when_add_environment_with_required_prefix_then_strips_prefix_from_keys() -> None:
    """Ensure add_environment(required_prefix=...) strips the prefix from resulting config keys."""
    os.environ['PREFIX_DATABASE_HOST'] = 'db.example.com'
    builder = appsettings2.ConfigurationBuilder()
    builder.add_environment(required_prefix='PREFIX_')
    configuration = builder.build()
    assert configuration is not None
    assert 'db.example.com' == configuration.get('DATABASE_HOST')
