#!/bin/bash
# SPDX-FileCopyrightText: © 2024 Shaun Wilson
# SPDX-License-Identifier: MIT
##
set -eo pipefail
python3 -m venv --prompt "appsettings2" .venv
source .venv/bin/activate
sed "s/0.0.0/$SEMVER/g" --in-place pyproject.toml
sed "s/0.0.0/$SEMVER/g" --in-place src/__init__.py
poetry build
poetry publish --repository=x4d-pypi
