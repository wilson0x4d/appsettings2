#!/bin/bash
# SPDX-FileCopyrightText: © 2024 Shaun Wilson
# SPDX-License-Identifier: MIT
set -eo pipefail
source .venv/bin/activate
if [[ "$1" == "" ]]; then
    pip install sphinx
fi
cd docs/
make html
