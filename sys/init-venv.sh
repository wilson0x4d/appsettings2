#!/bin/bash
# SPDX-FileCopyrightText: © 2024 Shaun Wilson
# SPDX-License-Identifier: MIT
#
# initializes the venv for the project in the current
# directory. installs poetry in that env for dep mgmt
# and then installs deps using poetry.
##
set -eo pipefail
python3 -m venv --prompt "appsettings2" .venv
source .venv/bin/activate
pip install poetry
if [ -e pyproject.toml ]; then
    poetry install --no-root
fi
deactivate
