# SPDX-FileCopyrightText: © 2024 Shaun Wilson
# SPDX-License-Identifier: MIT

from . import ConfigurationProvider
from .. import Configuration, ConfigurationException
from io import StringIO
import os
from typing import Any, TypeAlias
import yaml as _yaml

FileDescriptor: TypeAlias = int
any: TypeAlias = Any

class YamlConfigurationProvider(ConfigurationProvider):
    """Processes a yaml string, yaml file, or yaml stream and provides the content as Configuration data."""

    __obj:dict

    def __init__(self, filepath:str = None, *, yaml:str = None, fd:FileDescriptor = None, required:bool = True):
        if filepath:
            if os.path.isfile(filepath):
                with open(filepath, 'rt') as file:
                    self.__obj = _yaml.safe_load(file)
            elif required:
                raise ConfigurationException(f'Missing required file: {filepath}')
        elif fd:
            with open(fd, 'rt') as file:
                self.__obj = _yaml.safe_load(file)
        elif yaml:
            stream = StringIO(yaml)
            self.__obj = _yaml.safe_load(stream)
            stream.close()
        else:
            self.__obj = None

    def __populateRecursive(self, configuration:Configuration, prefix:str, o:dict):
        for kvp in o.items():
            if isinstance(kvp[1], dict):
                self.__populateRecursive(configuration, f'{prefix}__{kvp[0]}', kvp[1])
            else:
                configuration.set(f'{prefix}__{kvp[0]}', kvp[1])

    def populateConfiguration(self, configuration:Configuration):
        if self.__obj == None:
            return
        for kvp in self.__obj.items():
            if isinstance(kvp[1], dict):
                self.__populateRecursive(configuration, kvp[0], kvp[1])
            else:
                configuration.set(f'{kvp[0]}', kvp[1])
