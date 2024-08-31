# SPDX-FileCopyrightText: © 2024 Shaun Wilson
# SPDX-License-Identifier: MIT

from . import Configuration, ConfigurationException
from .providers import ConfigurationProvider
import typing

any: typing.TypeAlias = typing.Any

class ConfigurationBuilder:
    """A class which builds a Configuration object from one ore more ConfigurationProvider instances."""

    __normalize:bool
    __providers:list[ConfigurationProvider]

    def __init__(self, *, normalize:bool = False):
        self.__normalize = normalize
        self.__providers = []

    def addProvider(self, provider:ConfigurationProvider) -> 'ConfigurationBuilder':
        """Adds the specified provider to this builder instance."""
        if not provider:
            raise ConfigurationException('Missing required argument: provider')
        self.__providers.append(provider)
        return self

    def build(self) -> Configuration:
        """Builds a Configuration object from all providers which have been added to this builder."""
        configuration = Configuration(normalize=self.__normalize)
        for provider in self.__providers:
            provider.populateConfiguration(configuration)
        return configuration
