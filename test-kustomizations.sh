#!/usr/bin/env bash
#
# This script verifies whether the prepared kustomization files can be built.
# By default it looks for all kustomizations under current working directory,
# but it is possible to specify desired directories as the script's arguments.
#
# Usage:
#   ./test-kustomizations.sh [dir1 dir2 ...]
#
set -o errexit
set -o nounset
set -o pipefail

#
# Helper variables
#
BASE_DIR="$(dirname "$(readlink -f "$0")")"
COMMAND='kustomize'
ERRORS=0

RED="$(tput -T xterm setaf 1 || true)"
GREEN="$(tput -T xterm setaf 2 || true)"
YELLOW="$(tput -T xterm setaf 3 || true)"
RESET="$(tput -T xterm sgr0 || true)"


#
# Cleanup function for the script, trap ensures to execute it
#
function cleanup {
    tput -T xterm sgr0
}

trap cleanup EXIT


#
# Ensure the necessary tool is available
#
if ! command -v "${COMMAND}" &> /dev/null; then
    echo "${RED}ERROR Could not find command: ${COMMAND}${RESET}"
    exit 1
fi


#
# Verify files
#
if [ "$#" -eq 0 ]; then
    DIRS_TO_CHECK=('.')
else
    DIRS_TO_CHECK=("$@")
fi

mapfile -t FILES < <(find "${DIRS_TO_CHECK[@]}" \
                         -name 'kustomization.yaml' \
                         -o -name 'kustomization.yml' \
                         -o -name 'Kustomization')

for FILE in "${FILES[@]}"; do
    DIRECTORY=$(dirname "${FILE}")

    if ! OUTPUT=$("${COMMAND}" build "${DIRECTORY}" 2>&1); then
        echo "${RED}${FILE}: ERROR${RESET}"
        echo "${YELLOW}${OUTPUT}${RESET}"
        _=$(( ERRORS += 1 ))
    else
        echo "${GREEN}${FILE}: OK${RESET}"
    fi
done


#
# Set the exit status
#
echo -e '\n:: Summary'
if [ "${ERRORS}" -gt 0 ]; then
    echo "${RED}${ERRORS} errors!${RESET}"
    exit 1
else
    echo "${GREEN}No errors!${RESET}"
fi
