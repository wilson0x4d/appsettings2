"""A python library that unifies configuration sources into a `Configuration` object that can be bound to complex types, or accessed directly for configuration data."""
# SPDX-FileCopyrightText: © 2025 Shaun Wilson
# SPDX-License-Identifier: MIT

from .Configuration import Configuration
from .ConfigurationBuilder import ConfigurationBuilder
from .ConfigurationException import ConfigurationException
from .helpers import get_configuration, getConfiguration
from . import helpers
from . import providers


__version__ = '0.0.0'
__commit__ = '0abc123'
__all__ = [
    '__version__', '__commit__',
    'Configuration',
    'ConfigurationBuilder',
    'ConfigurationException',
    'get_configuration',
    'helpers',
    'providers',
    # deprecated since 2.0.0
    'getConfiguration'
]
