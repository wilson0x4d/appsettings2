# SPDX-FileCopyrightText: © 2025 Shaun Wilson
# SPDX-License-Identifier: MIT

import appsettings2
from punit import fact


@fact
def get_configuration_loads_all_variantions() -> None:
    """Assert that documented variations are loaded by default."""
    config = appsettings2.get_configuration(basename='tests/configs/appsettings')
    assert config.default is True
    assert config.prod is True
    assert config.staging is True
    assert config.qa is True
    assert config.dev is True
    assert config.local is True


@fact
def get_configuration_allows_disabling_variations() -> None:
    """Assert that we can disable loading of config variations by parameter."""
    config = appsettings2.get_configuration(basename='tests/configs/appsettings', variations=None)
    assert config.default is True  # NOTE: default/non-varied config is still expected to load
    assert config.get('prod', False) is False
    assert config.get('staging', False) is False
    assert config.get('qa', False) is False
    assert config.get('dev', False) is False
    assert config.get('local', False) is False
