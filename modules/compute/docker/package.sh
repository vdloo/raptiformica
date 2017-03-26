#!/bin/sh
set -e 

PACKAGED_DIR="$HOME/.raptiformica.d/var/packaged/docker"
mkdir -p "$PACKAGED_DIR/images"
cd "$PACKAGED_DIR"

# Make sure there is a checkout of the packaging code
if [ ! -d raptiformica ]; then
    git clone https://github.com/vdloo/raptiformica
else
    cd raptiformica
    git clean -xfd
    git reset --hard origin/master
    git pull origin master
    cd ..
fi

LOG_FILE="/tmp/$(uuidgen)"

# Provision the box
PYTHONPATH=raptiformica raptiformica/bin/raptiformica_spawn.py --compute-type docker --no-assimilate | tee $LOG_FILE

MACHINE_UUID=$(grep .raptiformica.d/var/machines/docker/headless/ $LOG_FILE  | head -n 1 | rev | cut -d '/' -f1 | rev)

# Change dir to the new check out
cd $HOME/.raptiformica.d/var/machines/docker/headless/$MACHINE_UUID/modules/compute/docker/

# Do not save an IP address in the packaged box
sudo docker exec $(cat container_id) rm -f /etc/cjdroute.conf

# Update the saved base image
sudo docker commit $(cat container_id) raptiformica-baseimage

# Kill the spawned Docker
sudo docker kill $(cat container_id)

# Clean up
cd "$PACKAGED_DIR"
PYTHONPATH=raptiformica raptiformica/bin/raptiformica_prune.py

