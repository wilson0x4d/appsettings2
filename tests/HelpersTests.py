# SPDX-FileCopyrightText: © 2025 Shaun Wilson
# SPDX-License-Identifier: MIT

import appsettings2
import os
from punit import fact


@fact
def get_configuration_env_prefix_filters_env_vars() -> None:
    """Ensure env_prefix filters environment variables to only those starting with the prefix."""
    os.environ['MYAPP_DATABASE_HOST'] = 'db.example.com'
    os.environ['DATABASE_HOST'] = 'other.example.com'  # should be filtered out
    config = appsettings2.get_configuration(basename='tests/configs/appsettings', env_prefix='MYAPP_')
    assert config is not None
    assert 'db.example.com' == config.get('DATABASE_HOST')
    assert config.get('MYAPP_DATABASE_HOST') is None


@fact
def get_configuration_env_prefix_strips_prefix_from_keys() -> None:
    """Ensure env_prefix strips the prefix from the resulting config keys."""
    os.environ['MYAPP_DATABASE_HOST'] = 'db.example.com'
    config = appsettings2.get_configuration(basename='tests/configs/appsettings', env_prefix='MYAPP_')
    assert config is not None
    assert 'db.example.com' == config.get('DATABASE_HOST')
    assert config.get('MYAPÍP_DATABASE_HOST') is None


@fact
def get_configuration_env_prefix_none_loads_all() -> None:
    """Ensure env_prefix=None loads all environment variables (backward compatible)."""
    os.environ['HELPER_TEST'] = 'passed'
    config = appsettings2.get_configuration(basename='tests/configs/appsettings', env_prefix=None)
    assert config is not None
    assert 'passed' == config.get('HELPER_TEST')


@fact
def get_configuration_loads_all_variantions() -> None:
    """Assert that documented variations are loaded by default."""
    config = appsettings2.get_configuration(basename='tests/configs/appsettings')
    assert config.default is True
    assert config.prod is True
    assert config.staging is True
    assert config.qa is True
    assert config.dev is True
    assert config.local is True


@fact
def get_configuration_allows_disabling_variations() -> None:
    """Assert that we can disable loading of config variations by parameter."""
    config = appsettings2.get_configuration(basename='tests/configs/appsettings', variations=None)
    assert config.default is True  # NOTE: default/non-varied config is still expected to load
    assert config.get('prod', False) is False
    assert config.get('staging', False) is False
    assert config.get('qa', False) is False
    assert config.get('dev', False) is False
    assert config.get('local', False) is False
