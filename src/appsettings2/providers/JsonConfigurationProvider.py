# SPDX-FileCopyrightText: © 2025 Shaun Wilson
# SPDX-License-Identifier: MIT

import json as _json
import os
from typing import Optional, TypeAlias
from ..Configuration import Configuration
from ..ConfigurationException import ConfigurationException
from .ConfigurationProvider import ConfigurationProvider


FileDescriptor: TypeAlias = int


class JsonConfigurationProvider(ConfigurationProvider):
    """A ``ConfigurationProvider`` that populates configuration data from JSON."""

    __obj: dict

    def __init__(self, filepath: Optional[str] = None, json: Optional[str] = None, fd: Optional[FileDescriptor] = None, required: bool = True) -> None:
        """
        Initialize ``JsonConfigurationProvider`` instance.

        The `filepath`, `json`, and `fd` parameters are mutually exclusive.

        :param filepath: Optional path to a JSON file used as a configuration source, defaults to None.
        :param json: Optional JSON string used as a configuration source, defaults to None.
        :param fd: Optional file descriptor (int) to be used as a configuration source, defaults to None.
        :param required: Optional parameter indicating whether the configuration source will raise `ConfigurationException` if the specified configuration source is missing, defaults to True.
        """
        obj = None
        try:
            if filepath:
                if os.path.isfile(filepath):
                    with open(filepath, 'rt') as file:
                        json = file.read()
                elif required:
                    raise ConfigurationException(f'Missing required file: {filepath}')
            elif fd:
                with open(fd, 'rt') as file:
                    json = file.read()
            if json:
                obj = _json.loads(json)
        finally:
            self.__obj = {} if obj is None else obj

    def __populate_recursive(self, configuration: Configuration, prefix: str, o: dict) -> None:
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


__all__ = ['JsonConfigurationProvider']
