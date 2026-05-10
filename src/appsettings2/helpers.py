# SPDX-FileCopyrightText: © 2025 Shaun Wilson
# SPDX-License-Identifier: MIT

import pathlib
from typing import Optional

from .Configuration import Configuration
from .ConfigurationBuilder import ConfigurationBuilder


def get_configuration(basename: str | pathlib.PosixPath | pathlib.Path = 'appsettings', json: bool = True, toml: bool = True, yaml: bool = True, cli: bool = True, environment: bool = True, variations: Optional[list[str | None]] = ['', 'prod', 'production', 'stage', 'staging', 'qa', 'dev', 'development', 'local']) -> Configuration:
    """
    Get a ``Configuration`` instance by loading from a set of well-known providers and their variations.

    :param basename: Base filename used with file-based configuration providers, defaults to 'appsettings'.
    :param json: ``True`` to load configuration from JSON files, defaults to True
    :param toml: ``True`` to load configuration from TOML files, defaults to True
    :param yaml: ``True`` to load configuration from YAML files, defaults to True
    :param cli: ``True`` to load configuration from Command-Line, defaults to True
    :param environment: ``True`` to load configuration from process Environment, defaults to True
    :param variations: A set of variations to apply to use with file-based Configuration Providers, defaults to ['', 'prod', 'production', 'stage', 'staging', 'qa', 'dev', 'development', 'local']
    :return: An ``appsettings2.Configuration`` instance.
    """
    if type(basename) is pathlib.Path or type(basename) is pathlib.PosixPath:
        basename = str(basename)
    builder = ConfigurationBuilder()
    variations = variations if variations is not None and len(variations) > 0 else [None]
    for variation in variations:
        variation = f'.{variation}' if variation is not None and len(variation) > 0 else ''
        if json:
            builder.add_json(f'{basename}{variation}.json', required=False)
        if toml:
            builder.add_toml(f'{basename}{variation}.toml', required=False)
        if yaml:
            builder.add_yaml(f'{basename}{variation}.yaml', required=False)
    if cli:
        builder.add_command_line()
    if environment:
        builder.add_environment()
    return builder.build()


getConfiguration = get_configuration  # noqa: N816
"""⚠️ DEPRECATED: use ``get_configuration(...)`` instead."""
