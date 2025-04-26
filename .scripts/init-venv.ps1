#!/bin/pwsh
# SPDX-FileCopyrightText: Copyright (C) Shaun Wilson
# SPDX-License-Identifier: MIT
$ErrorActionPreference = "Stop"
if ($env:PYTHON_VERSION -ne "") {
    $PYPATH=$(Get-Command "python$env:PYTHON_VERSION").Source
} else {
    $PYPATH=$(Get-Command "python3").Source
}
& $PYPATH -m venv --prompt "appsettings2" .venv-pwsh
. .\.venv-pwsh\Scripts\Activate.ps1
& python -m pip install -r requirements-dev.txt
deactivate
