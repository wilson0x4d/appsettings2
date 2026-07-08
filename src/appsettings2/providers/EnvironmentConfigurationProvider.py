# SPDX-FileCopyrightText: © 2025 Shaun Wilson
# SPDX-License-Identifier: MIT

import os
from typing import Any

from ..Configuration import Configuration
from .ConfigurationProvider import ConfigurationProvider


class EnvironmentConfigurationProvider(ConfigurationProvider):
    """A ``ConfigurationProvider`` that populates configuration data from Environment variables."""

    __required_prefix: str | None

    def __init__(self, /, required_prefix: str | None = None, **kwargs: Any) -> None:
        self.__required_prefix = required_prefix.upper() if required_prefix is not None else None

    def populate_configuration(self, configuration: Configuration) -> None:
        """
        Populate the provided :py:class:`~appsettings2.Configuration` from environment variables.

        Usage::

            # All env vars become config keys:
            provider = EnvironmentConfigurationProvider()
            provider.populate_configuration(config)

            # Only keys with a specific prefix, stripped in output:
            provider = EnvironmentConfigurationProvider(required_prefix="APP_")
            # APP_DATABASE_URL=postgres://...  →  config["DATABASE_URL"] == "postgres://..."
            provider.populate_configuration(config)

        When ``required_prefix`` is set, only keys starting with that prefix are included,
        and the prefix is stripped from each key in the output configuration.
        """
        for k in os.environ:
            key = (
                k
                if self.__required_prefix is None
                else k[len(self.__required_prefix):]
            )
            configuration.set(key, os.environ[k])
