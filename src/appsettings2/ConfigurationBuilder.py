# SPDX-FileCopyrightText: © 2025 Shaun Wilson
# SPDX-License-Identifier: MIT

from typing import Any, Optional, TypeAlias

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


FileDescriptor: TypeAlias = int


class ConfigurationBuilder:
    """
    Build a :py:class:`~appsettings2.Configuration` object from one or more :py:class:`~appsettings2.providers.ConfigurationProvider` instances.
    """

    __disable_events: bool | None
    __normalize: bool
    __providers: list[ConfigurationProvider]
    __watcher: Any

    def __init__(self, normalize: bool = False, scrubkeys: bool = False, disable_events: bool | None = None, watcher: Any = None) -> None:
        """
        Initialize *ConfigurationBuilder* instance.

        :param normalize: Option indicating whether or not attribute names should be normalized to upper-case on the resulting :py:class:`~appsettings2.Configuration` object, defaults to False.
        :param scrubkeys: Option indicating whether or not attribute names should be scrubbed to be compatible with the Python lexer, defaults to False.
        :param disable_events: Option indicating whether change events should be emitted, defaults to None.
        :param watcher: Optional :py:class:`~appsettings2.ConfigurationWatcher` to associate with the built configuration.
        """
        self.__disable_events = disable_events
        self.__normalize = normalize
        self.__scrubkeys = scrubkeys
        self.__providers = []
        self.__watcher = watcher

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
 
    def add_environment(self, required_prefix: str | None = None) -> 'ConfigurationBuilder':
        """
        Add a :py:class:`~appsettings2.providers.EnvironmentConfigurationProvider`.

        :param required_prefix: Optional prefix used to filter which environment variables are included. Only variables whose names start with this prefix (followed by ``_`` or ``__``) will be loaded. When ``None``, all environment variables are included. Defaults to None.
        :return: Returns :py:class:`~appsettings2.ConfigurationBuilder` for method chaining.
        """
        return self.add_provider(EnvironmentConfigurationProvider(required_prefix=required_prefix))

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

    def disable_events(self) -> 'ConfigurationBuilder':
        """
        Disable change events for the built :py:class:`~appsettings2.Configuration`.

        :return: Returns :py:class:`~appsettings2.ConfigurationBuilder` for method chaining.
        """
        self.__disable_events = True
        return self

    def disableEvents(self) -> 'ConfigurationBuilder':
        """⚠️ DEPRECATED: use ``disable_events(...)`` instead."""
        return self.disable_events()

    def enable_watcher(self) -> 'ConfigurationBuilder':
        """
        Create and assign a :py:class:`~appsettings2.ConfigurationWatcher` instance to the builder.

        Only creates a new watcher if ``self.__watcher`` is ``None``.

        :return: Returns :py:class:`~appsettings2.ConfigurationBuilder` for method chaining.
        """
        if self.__watcher is None:
            from .ConfigurationWatcher import ConfigurationWatcher
            self.__watcher = ConfigurationWatcher()
        return self

    def build(self, disable_events: bool | None = None, watcher: Any = None) -> Configuration:
        """
        Builds a `Configuration` object using the providers which have been added to the builder.

        :param disable_events: Option indicating whether change events should be emitted, defaults to None (uses value from ``__init__``).
        :param watcher: Optional :py:class:`~appsettings2.ConfigurationWatcher`, defaults to None (uses value from ``__init__``).
        :return: A `Configuration` object, populated with configuration data.
        """
        effective_watcher = watcher if watcher is not None else self.__watcher
        configuration = Configuration(
            normalize=self.__normalize,
            scrubkeys=self.__scrubkeys,
            disable_events=disable_events if disable_events is not None else self.__disable_events,
            watcher=effective_watcher)
        for provider in self.__providers:
            provider.populate_configuration(configuration)
        if effective_watcher is not None:
            for provider in self.__providers:
                fp = getattr(provider, 'filepath', None)
                if fp is not None:
                    effective_watcher.add_watch(fp)
        return configuration


__all__ = ['ConfigurationBuilder']
