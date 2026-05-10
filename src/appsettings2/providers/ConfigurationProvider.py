# SPDX-FileCopyrightText: © 2025 Shaun Wilson
# SPDX-License-Identifier: MIT

from ..Configuration import Configuration
from abc import ABC, abstractmethod
from typing import final


class ConfigurationProvider(ABC):
    """The abstract base class which all Configuration Providers implement."""

    @abstractmethod
    def populate_configuration(self, configuration: Configuration) -> None:
        """Populate the provided :py:class:`~appsettings2.Configuration` object using provider-specific methods."""
        ...

    @final
    def populateConfiguration(self, configuration: Configuration) -> None:  # noqa: N802
        """⚠️ DEPRECATED: use ``populate_configuration(...)`` instead."""
        self.populate_configuration(configuration)
