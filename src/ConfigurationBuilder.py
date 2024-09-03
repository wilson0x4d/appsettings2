# SPDX-FileCopyrightText: © 2024 Shaun Wilson
# SPDX-License-Identifier: MIT

from .Configuration import Configuration
from .ConfigurationException import ConfigurationException
from .providers import ConfigurationProvider
import typing

type any = typing.Any

class ConfigurationBuilder:
    """
    Builds a :py:class:`~appsettings2.Configuration` object from one or more :py:class:`~appsettings2.providers.ConfigurationProvider` instances.
    """

    __normalize:bool
    __providers:list[ConfigurationProvider]

    def __init__(self, *, normalize:bool = False, scrubkeys:bool = False):
        """
        :param normalize: Option indicating whether or not attribute names should be normalized to upper-case on the resulting :py:class:`~appsettings2.Configuration` object, defaults to False.
        :param scrubkeys: Option indicating whether or not attribute names (and key names) should be scrubbed to be compatible with the Python lexer, defaults to False.
        """
        self.__normalize = normalize
        self.__scrubkeys = scrubkeys
        self.__providers = []

    def addProvider(self, provider:ConfigurationProvider) -> 'ConfigurationBuilder':
        """
        Adds the specified `ConfigurationProvider` object to the builder.
        Can be called multiple times to add multiple providers.

        :param provider: A class implementing the `ConfigurationProvider` abstract class.
        :return: Returns `ConfigurationBuilder` for method chaining.
        """
        if provider == None or not issubclass(type(provider), ConfigurationProvider):
            raise ConfigurationException('Missing/Invalid argument: provider')
        self.__providers.append(provider)
        return self

    def build(self) -> Configuration:
        """
        Builds a `Configuration` object using the providers which have been added to the builder.

        :return: A `Configuration` object, populated with configuration data.
        """
        configuration = Configuration(normalize=self.__normalize, scrubkeys=self.__scrubkeys)
        for provider in self.__providers:
            provider.populateConfiguration(configuration)
        return configuration
