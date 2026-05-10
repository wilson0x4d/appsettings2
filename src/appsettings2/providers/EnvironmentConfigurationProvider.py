# SPDX-FileCopyrightText: © 2025 Shaun Wilson
# SPDX-License-Identifier: MIT

from .ConfigurationProvider import ConfigurationProvider
from ..Configuration import Configuration
import os


class EnvironmentConfigurationProvider(ConfigurationProvider):
    """A ``ConfigurationProvider`` that populates configuration data from Environment variables."""

    def populate_configuration(self, configuration: Configuration) -> None:  # noqa: D102
        for k in os.environ:
            configuration.set(k, os.environ[k])
