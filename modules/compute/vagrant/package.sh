#!/bin/sh
set -e 

PACKAGED_DIR="$HOME/.raptiformica.d/var/packaged/vagrant"
mkdir -p "$PACKAGED_DIR/images"
cd "$PACKAGED_DIR"

# make sure there is a checkout of the packaging code
if [ ! -d raptiformica ]; then
    git clone https://github.com/vdloo/raptiformica
else
    cd raptiformica
    git clean -xfd
    git reset --hard origin/master
    git pull origin master
    cd ..
fi

# make sure we have a vagrant-catalog-generator checkout
if [ ! -d vagrant-catalog-generator ]; then
    git clone https://github.com/ByteInternet/vagrant-catalog-generator
else
    cd vagrant-catalog-generator
    git clean -xfd
    git reset --hard origin/master
    git pull origin master
    cd ..
fi;

LOG_FILE="/tmp/$(uuidgen)"

# Provision the box
PYTHONPATH=raptiformica raptiformica/bin/raptiformica_spawn.py --compute-type vagrant --no-assimilate | tee $LOG_FILE

MACHINE_UUID=$(grep .raptiformica.d/var/machines/vagrant/headless/ $LOG_FILE  | head -n 1 | rev | cut -d '/' -f1 | rev)

# Change dir to the new check out
cd $HOME/.raptiformica.d/var/machines/vagrant/headless/$MACHINE_UUID/modules/compute/vagrant/

# Do not save an IP address in the packaged box
vagrant ssh -c "sudo rm -f /etc/cjdroute.conf"

# Package the running instance
vagrant package

# Incremental images
RELEASE=$(find "$PACKAGED_DIR/images" | wc -l)
mv package.box "$PACKAGED_DIR/images/compute_headless_vagrant.virtualbox.release-${RELEASE}.box"

cd "$PACKAGED_DIR"
# clean up old boxfiles, keep up to 5 releases
(cd vagrant-catalog-generator; export PYTHONPATH=.; \
    python bin/prune_boxfiles.py \
    --directory ../images --amount 5)

# generate the catalog.json with a filepath as url
(cd vagrant-catalog-generator; export PYTHONPATH=.; \
    python bin/generate_catalog.py \
    --directory ../images --base-url file://`pwd`/../images \
    --description "default vagrant compute type" --name compute_headless_vagrant)

# Change back to the checkout to upgrade the box locally
cd $HOME/.raptiformica.d/var/machines/vagrant/headless/$MACHINE_UUID/modules/compute/vagrant/
vagrant box update || /bin/true

# Clean up
cd "$PACKAGED_DIR"
PYTHONPATH=raptiformica raptiformica/bin/raptiformica_prune.py

