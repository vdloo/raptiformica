#!/bin/sh
set -e 

PACKAGED_DIR="$HOME/.raptiformica.d/var/packaged/docker"
mkdir -p "$PACKAGED_DIR/images"
cd "$PACKAGED_DIR"

# make sure there is a checkout of the packaging code
if [ ! -d raptiformica ]; then
    git clone --recursive https://github.com/vdloo/raptiformica
else
    cd raptiformica
    git clean -xfd
    git reset --hard origin/master
    git pull origin master
    cd ..
fi

# Provision the box
PYTHONPATH=raptiformica raptiformica/bin/raptiformica_spawn.py --compute-type docker --no-assimilate | tee $LOG_FILE

MACHINE_UUID=$(grep .raptiformica.d/var/machines/docker/headless/ $LOG_FILE  | head -n 1 | rev | cut -d '/' -f1 | rev)

# Change dir to the new check out
cd $HOME/.raptiformica.d/var/machines/docker/headless/$MACHINE_UUID/modules/compute/docker/

# Update the saved base image
sudo docker commit $(cat container_id) raptiformica-baseimage

# Clean up
cd "$PACKAGED_DIR"
PYTHONPATH=raptiformica raptiformica/bin/raptiformica_prune.py
