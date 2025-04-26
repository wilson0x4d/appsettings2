#!/bin/bash
# SPDX-FileCopyrightText: Copyright (C) Shaun Wilson
# SPDX-License-Identifier: MIT
set -eo pipefail
if [[ "$PYTHON_VERSION" != "" ]]; then
    PYPATH=`which python$PYTHON_VERSION`
else
    PYPATH="python3"
fi
$PYPATH -m venv --prompt "appsettings2" .venv-bash
source .venv-bash/bin/activate
if [ -f requirements-dev.txt ]; then
    pip install -r requirements-dev.txt
fi
if ! [ -f requirements-dev.txt ]; then
    pip install -r requirements.txt
fi
deactivate
