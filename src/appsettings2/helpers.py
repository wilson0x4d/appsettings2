# SPDX-FileCopyrightText: © 2025 Shaun Wilson
# SPDX-License-Identifier: MIT

import pathlib
from typing import Optional

from .Configuration import Configuration
from .ConfigurationBuilder import ConfigurationBuilder
from .providers import *


def getConfiguration(baseName:str|pathlib.PosixPath|pathlib.Path = 'appsettings', json:bool = True, toml:bool = True, yaml:bool = True, cli:bool = True, environment:bool = True, variations:Optional[list[str|None]] = ['', 'prod', 'production', 'stage', 'staging', 'qa', 'dev', 'development', 'local']) -> Configuration:
    if type(baseName) is pathlib.Path or type(baseName) is pathlib.PosixPath:
        baseName = str(baseName)
    builder:ConfigurationBuilder = ConfigurationBuilder()
    variations = variations if variations is not None and len(variations) > 0 else [None]
    for variation in variations:
        variation = f'.{variation}' if variation is not None and len(variation) > 0 else ''
        if json:
            builder.addJson(f'{baseName}{variation}.json', required=False)
        if toml:
            builder.addToml(f'{baseName}{variation}.toml', required=False)
        if yaml:
            builder.addYaml(f'{baseName}{variation}.yaml', required=False)
    if cli:
        builder.addCommandLine()
    if environment:
        builder.addEnvironment()
    return builder.build()
