# SPDX-FileCopyrightText: © 2025 Shaun Wilson
# SPDX-License-Identifier: MIT

from typing import Optional


class ConfigurationException(Exception):
    """An exception raised by ``appsettings2`` library."""

    def __init__(self, reason: Optional[str] = None) -> None:
        self.reason = reason or 'A configuration error occurred.'
        super().__init__(self.reason)
