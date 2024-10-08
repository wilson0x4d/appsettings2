#!/bin/bash
# SPDX-FileCopyrightText: © 2024 Shaun Wilson
# SPDX-License-Identifier: MIT
##
set -eo pipefail
source .venv/bin/activate
python -m unittest discover -s tests -p '*Tests.py' -k '*Test*' -k '*test*'
