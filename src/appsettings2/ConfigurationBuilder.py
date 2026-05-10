# SPDX-FileCopyrightText: © 2025 Shaun Wilson
# SPDX-License-Identifier: MIT

from .Configuration import Configuration
from .ConfigurationException import ConfigurationException
from .providers import (
    CommandLineConfigurationProvider,
    ConfigurationProvider,
    EnvironmentConfigurationProvider,
    JsonConfigurationProvider,
    TomlConfigurationProvider,
    YamlConfigurationProvider,
)
from typing import Optional, TypeAlias


FileDescriptor: TypeAlias = int


class ConfigurationBuilder:
    """
    Build a :py:class:`~appsettings2.Configuration` object from one or more :py:class:`~appsettings2.providers.ConfigurationProvider` instances.
    """

    __normalize: bool
    __providers: list[ConfigurationProvider]

    def __init__(self, normalize: bool = False, scrubkeys: bool = False) -> None:
        """
        Initialize *ConfigurationBuilder* instance.

        :param normalize: Option indicating whether or not attribute names should be normalized to upper-case on the resulting :py:class:`~appsettings2.Configuration` object, defaults to False.
        :param scrubkeys: Option indicating whether or not attribute names should be scrubbed to be compatible with the Python lexer, defaults to False.
        """
        self.__normalize = normalize
        self.__scrubkeys = scrubkeys
        self.__providers = []

    def add_provider(self, provider: ConfigurationProvider) -> 'ConfigurationBuilder':
        """
        Add the specified `ConfigurationProvider` object to the builder.

        Can be called multiple times to add multiple providers.

        :param provider: A class implementing the `ConfigurationProvider` abstract class.
        :return: Returns :py:class:`~appsettings2.ConfigurationBuilder` for method chaining.
        """
        if provider is None or not issubclass(type(provider), ConfigurationProvider):
            raise ConfigurationException('Missing/Invalid argument: provider')
        self.__providers.append(provider)
        return self

    addProvider = add_provider
    """⚠️ DEPRECATED: use ``add_provider(...)`` instead."""

    def add_command_line(self, argv=None) -> 'ConfigurationBuilder':
        """
        Add a :py:class:`~appsettings2.providers.CommandLineConfigurationProvider`, optionally overriding ``argv``.

        :param argv: Optional override of ``sys.argv``, defaults to None.
        :return: Returns :py:class:`~appsettings2.ConfigurationBuilder` for method chaining.
        """
        return self.add_provider(CommandLineConfigurationProvider(argv=argv))

    addCommandLine = add_command_line
    """⚠️ DEPRECATED: use ``add_command_line(...)`` instead."""
 
    def add_environment(self) -> 'ConfigurationBuilder':
        """
        Add a :py:class:`~appsettings2.providers.EnvironmentConfigurationProvider`.

        :return: Returns :py:class:`~appsettings2.ConfigurationBuilder` for method chaining.
        """
        return self.add_provider(EnvironmentConfigurationProvider())

    addEnvironment = add_environment
    """⚠️ DEPRECATED: use ``add_environment(...)`` instead."""

    def add_json(self, filepath: Optional[str] = None, json: Optional[str] = None, fd: Optional[FileDescriptor] = None, required: bool = True) -> 'ConfigurationBuilder':
        """
        Add a :py:class:`~appsettings2.providers.JsonConfigurationProvider`.

        The `filepath`, `json`, and `fd` parameters are mutually exclusive.

        :param filepath: Optional path to a JSON file used as a configuration source, defaults to None.
        :param json: Optional JSON string used as a configuration source, defaults to None.
        :param fd: Optional file descriptor (int) to be used as a configuration source, defaults to None.
        :param required: Optional parameter indicating whether the configuration source will raise `ConfigurationException` if the specified configuration source is missing, defaults to True.
        :return: Returns :py:class:`~appsettings2.ConfigurationBuilder` for method chaining.
        """
        return self.add_provider(JsonConfigurationProvider(filepath=filepath, json=json, fd=fd, required=required))

    addJson = add_json
    """⚠️ DEPRECATED: use ``add_json(...)`` instead."""

    def add_toml(self, filepath: Optional[str] = None, toml: Optional[str] = None, fd: Optional[FileDescriptor] = None, required: bool = True) -> 'ConfigurationBuilder':
        """
        Adds a :py:class:`~appsettings2.providers.TomlConfigurationProvider`.

        The `filepath`, `toml`, and `fd` parameters are mutually exclusive.

        :param filepath: Optional path to a TOML file used as a configuration source, defaults to None.
        :param toml: Optional TOML string used as a configuration source, defaults to None.
        :param fd: Optional file descriptor (int) to be used as a configuration source, defaults to None.
        :param required: Optional parameter indicating whether the configuration source will raise `ConfigurationException` if the specified configuration source is missing, defaults to True.
        :return: Returns :py:class:`~appsettings2.ConfigurationBuilder` for method chaining.
        """
        return self.add_provider(TomlConfigurationProvider(filepath=filepath, toml=toml, fd=fd, required=required))

    addToml = add_toml
    """⚠️ DEPRECATED: use ``add_toml(...)`` instead."""

    def add_yaml(self, filepath: Optional[str] = None, yaml: Optional[str] = None, fd: Optional[FileDescriptor] = None, required: bool = True) -> 'ConfigurationBuilder':
        """
        Adds a :py:class:`~appsettings2.providers.YamlConfigurationProvider`.

        The `filepath`, `yaml`, and `fd` parameters are mutually exclusive.

        :param filepath: Optional path to a YAML file used as a configuration source, defaults to None.
        :param yaml: Optional YAML string used as a configuration source, defaults to None.
        :param fd: Optional file descriptor (int) to be used as a configuration source, defaults to None.
        :param required: Optional parameter indicating whether the configuration source will raise `ConfigurationException` if the specified configuration source is missing, defaults to True.
        :return: Returns :py:class:`~appsettings2.ConfigurationBuilder` for method chaining.
        """
        return self.add_provider(YamlConfigurationProvider(filepath=filepath, yaml=yaml, fd=fd, required=required))

    addYaml = add_yaml
    """⚠️ DEPRECATED: use ``add_yaml(...)`` instead."""

    def build(self) -> Configuration:
        """
        Builds a `Configuration` object using the providers which have been added to the builder.

        :return: A `Configuration` object, populated with configuration data.
        """
        configuration = Configuration(
            normalize=self.__normalize, scrubkeys=self.__scrubkeys)
        for provider in self.__providers:
            provider.populate_configuration(configuration)
        return configuration


__all__ = ['ConfigurationBuilder']
