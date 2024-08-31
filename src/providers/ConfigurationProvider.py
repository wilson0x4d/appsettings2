# SPDX-FileCopyrightText: © 2024 Shaun Wilson
# SPDX-License-Identifier: MIT

from .. import Configuration
from abc import ABC as abstract, abstractmethod

class ConfigurationProvider(abstract):

    @abstractmethod
    def populateConfiguration(self, configuration:Configuration) -> None:
        """The ConfigurationProvider will populate the provided Configuration instance."""
        pass
