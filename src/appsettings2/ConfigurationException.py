# SPDX-FileCopyrightText: © 2025 Shaun Wilson
# SPDX-License-Identifier: MIT

from typing import Optional


class ConfigurationException(Exception):
    """An exception raised by `appsettings2` library."""
    def __init__(self, reason:Optional[str] = None):
        super().__init__(reason)
