#!/bin/pwsh
# SPDX-FileCopyrightText: Copyright (C) Shaun Wilson
# SPDX-License-Identifier: MIT
$missingVenv = $env:VIRTUAL_ENV -eq $null
if ($missingVenv) {
    & .\.venv-pwsh\Scripts\Activate.ps1
}
python -m punit --verbose --trait '!integration' --trait '!hardcoded' --trait '!longrunning' --trait '!manual'
if ($missingVenv) {
    deactivate
}
