# SPDX-FileCopyrightText: © 2025 Shaun Wilson
# SPDX-License-Identifier: MIT

import os
import tomllib as _toml
from typing import Any, Optional, TypeAlias

from .ConfigurationProvider import ConfigurationProvider
from ..Configuration import Configuration
from ..ConfigurationException import ConfigurationException


FileDescriptor: TypeAlias = int


class TomlConfigurationProvider(ConfigurationProvider):
    """A ``ConfigurationProvider`` that populates configuration data from TOML."""

    __filepath: str | None
    __obj: dict[str, Any]

    def __init__(self, filepath: Optional[str] = None, toml: Optional[str] = None, fd: Optional[FileDescriptor] = None, required: bool = True) -> None:
        """
        Initialize a ``TomlConfigurationProvider`` instance.

        The `filepath`, `toml`, and `fd` parameters are mutually exclusive.

        :param filepath: Optional path to a TOML file used as a configuration source, defaults to None.
        :param toml: Optional TOML string used as a configuration source, defaults to None.
        :param fd: Optional file descriptor (int) to be used as a configuration source, defaults to None.
        :param required: Optional parameter indicating whether the configuration source will raise `ConfigurationException` if the specified configuration source is missing, defaults to True.
        """
        self.__filepath = filepath
        obj = None
        try:
            if filepath:
                if os.path.isfile(filepath):
                    with open(filepath, 'rt') as file:
                        toml = file.read()
                elif required:
                    raise ConfigurationException(f'Missing required file: {filepath}')
            elif fd:
                with open(fd, 'rt') as file:
                    toml = file.read()
            if toml:
                obj = _toml.loads(toml)
        finally:
            self.__obj = {} if obj is None else obj

    def __populate_recursive(self, configuration: Configuration, prefix: str, o: dict[str, Any]) -> None:
        for kvp in o.items():
            if isinstance(kvp[1], dict):
                self.__populate_recursive(configuration, f'{prefix}__{kvp[0]}', kvp[1])
            else:
                configuration.set(f'{prefix}__{kvp[0]}', kvp[1])

    def populate_configuration(self, configuration: Configuration) -> None:  # noqa: D102
        if self.__obj is None:
            return
        for kvp in self.__obj.items():
            if isinstance(kvp[1], dict):
                self.__populate_recursive(configuration, kvp[0], kvp[1])
            else:
                configuration.set(f'{kvp[0]}', kvp[1])

    @property
    def filepath(self) -> str | None:
        """The file path used to initialize this provider, or ``None``."""
        return self.__filepath


__all__ = ['TomlConfigurationProvider']
