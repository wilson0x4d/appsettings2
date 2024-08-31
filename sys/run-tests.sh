#!/bin/bash
# SPDX-FileCopyrightText: © 2024 Shaun Wilson
# SPDX-License-Identifier: MIT
##
set -eo pipefail
python3 -m venv --prompt "appsettings2" .venv
source .venv/bin/activate
python -m unittest discover -s tests -p '*Tests.py' -k '*Test*' -k '*test*'
