#!/bin/bash

# By using this script, you agree to the
# RailSem19 license agreement:
# https://wilddash.cc/license/railsem19
# -------------------------------------------------------------------

DOWNL_SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"
bash ${DOWNL_SCRIPT_DIR}/download_wilddash_file.sh wd_public_v2p0.zip ./
bash ${DOWNL_SCRIPT_DIR}/download_wilddash_file.sh wd_both_02.zip ./
DOWNL_SCRIPT_DIR=