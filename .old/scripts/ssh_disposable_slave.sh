#!/bin/bash
DIRECTORY_NAME="$( cd "$(dirname "${BASH_SOURCE[0]}" )" && pwd )"
MACHINE_DIR="$DIRECTORY_NAME/../machines/"
RANDOM_MACHINE_DIR="$(find $MACHINE_DIR -maxdepth 1 -mindepth 1 -type d | shuf -n 1)"
cd "$RANDOM_MACHINE_DIR/vagrantfiles/headless"
vagrant ssh
