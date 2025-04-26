#!/bin/bash
# SPDX-FileCopyrightText: © 2024 Shaun Wilson
# SPDX-License-Identifier: MIT
##
set -eo pipefail
python3 -m venv --prompt "appsettings2" .venv-bash
source .venv-bash/bin/activate
sed "s/0.0.0/$SEMVER/g" --in-place pyproject.toml
sed "s/0.0.0/$SEMVER/g" --in-place appsettings2/__init__.py
rm -rf build/
rm -rf dist/
rm -rf *.egg-info/
python3 -m build
python3 -m twine upload --repository $PYPI_REPO dist/*
