# SPDX-FileCopyrightText: © 2025 Shaun Wilson
# SPDX-License-Identifier: MIT

import appsettings2
from punit import fact


@fact
def getConfigurationLoadsVariations() -> None:
    """verify that documented variations are loaded by default."""
    config = appsettings2.getConfiguration(baseName='tests/configs/appsettings')
    assert True == config.default
    assert True == config.prod
    assert True == config.staging
    assert True == config.qa
    assert True == config.dev
    assert True == config.local

@fact
def getConfigurationCanDisableVariations() -> None:
    """verify that we can disable loading of config variations by parameter."""
    config = appsettings2.getConfiguration(baseName='tests/configs/appsettings', variations=None)
    assert True == config.default # NOTE: default/non-varied config is still expected to load
    assert False == config.get('prod', False)
    assert False == config.get('staging', False)
    assert False == config.get('qa', False)
    assert False == config.get('dev', False)
    assert False == config.get('local', False)
