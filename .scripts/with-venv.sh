#!/bin/bash
# SPDX-FileCopyrightText: © 2024 Shaun Wilson
# SPDX-License-Identifier: MIT
#
# use this script to drop into a venv, this
# is designed to be used as an --rcfile target
# for containers, or for manual/direct use.
#
# this script needs to be sourced or rc'd into
# the shell to work correctly, fx:
#
# source .scripts/with-venv.sh
#
##
source ~/.bashrc
export PS1='\$ '
echo -n -e "\033]0;appsettings2\007"
source .venv-bash/bin/activate
