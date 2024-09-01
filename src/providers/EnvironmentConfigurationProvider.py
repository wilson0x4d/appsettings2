# SPDX-FileCopyrightText: © 2024 Shaun Wilson
# SPDX-License-Identifier: MIT

from .ConfigurationProvider import ConfigurationProvider
from ..Configuration import Configuration
import os

class EnvironmentConfigurationProvider(ConfigurationProvider):
    """Processes environment variables and provides them as Configuration data."""

    def populateConfiguration(self, configuration:Configuration):
        for k in os.environ:
            configuration.set(k, os.environ[k])
