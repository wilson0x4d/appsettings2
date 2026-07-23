# SPDX-FileCopyrightText: © 2025 Shaun Wilson
# SPDX-License-Identifier: MIT

import appsettings2
import os
from punit import fact, inlinedata, theory


class EnvironmentConfigurationProviderTests:

    @fact
    def basic_verification(self) -> None:
        os.environ['ENV_TEST'] = '1'
        os.environ['some_subobj__ENV_TEST'] = '2'
        provider = appsettings2.providers.EnvironmentConfigurationProvider()
        configuration = appsettings2.Configuration()
        provider.populateConfiguration(configuration)
        assert '1' == configuration.get('ENV_TEST')
        assert '2' == configuration.get('some_subobj:ENV_TEST')

    @theory
    @inlinedata()
    def required_prefix_performs_filter(self, when: str, required_prefix: str | None, then_value: str) -> None:
        """basic verification for `required_prefix` logic"""
        if required_prefix is None:
            os.environ['DATABASE_HOST'] = 'db.example.com'
        else:
            os.environ[f'{required_prefix}DATABASE_HOST'] = 'db.example.com'
        os.environ['DATABASE_HOST'] = 'other.example.com'
        provider = appsettings2.providers.EnvironmentConfigurationProvider(required_prefix=required_prefix)
        configuration = appsettings2.Configuration()
        provider.populate_configuration(configuration)
        assert then_value == configuration.get('DATABASE_HOST')
        assert configuration.get('OTHER:DATABASE_HOST') is None

    @fact
    def required_prefix_stripped_from_key(self) -> None:
        """Ensure the required prefix is stripped from the resulting config key."""
        os.environ['APP_DATABASE_HOST'] = 'db.example.com'
        provider = appsettings2.providers.EnvironmentConfigurationProvider(required_prefix='APP_')
        configuration = appsettings2.Configuration()
        provider.populateConfiguration(configuration)
        assert 'db.example.com' == configuration.get('DATABASE_HOST')

    @fact
    def required_prefix_none_passes_all(self) -> None:
        """Ensure required_prefix=None passes all env vars (backward compatible)."""
        os.environ['ENV_TEST'] = 'value'
        provider = appsettings2.providers.EnvironmentConfigurationProvider(required_prefix=None)
        configuration = appsettings2.Configuration()
        provider.populateConfiguration(configuration)
        assert 'value' == configuration.get('ENV_TEST')
