Raptiformica
============

Decentralized server orchestration

## What is this?

This project is an experimental framework for creating a virtual
data center from interlinked machines and provides a configuration 
system where provisioning scripts, compute back-ends and rules for 
orchestration can be combined to build dynamic platforms that 
expand or gracefully degrade based on the resources available.

For example: if a rule is configured that there should be
at least three servers online (required for Raft consensus in consul), 
then the system should spawn a new machine if necessary on a compute 
back-end if one is available somewhere in the network. 

## Principles

There are a couple of fundamentals on which this project is based.

### The decentralized network

Any machine can join the network as long as at least one other machine in
the network can reach it. This allows for the creation of a virtual
data center using scattered resources. When moving machines can participate 
in the network (laptops, rooted Androids running Linux even), available
computing power can be leveraged which otherwise might be difficult due to
networking and routing. 

Distributed applications often assume they are being run in a zone in a data 
center where every machine can reach every machine. This makes the barrier of 
entry high for using such applications, requiring the user to procure an
environment that satisfies those requirements. Usually the easiest way to
do so is to boot a select number of instances at a random cloud provider.

This is unfortunate because every random tinkerer can probably scrape enough 
computing power together in their bedroom in the form of old desktops or has 
a handful of cheap VPS instances at various cloud providers. Raptiformica
tries to solve that problem by making it easy to mesh those machines
together and form a virtual data center as a plateau to build your
infrastructure on.

### All machines can bootstrap

As long as there is at least one machine left alive, the entire platform
should be able to automatically be re-created as soon as new resources
become available. When enough machines perish, data could be lost but the 
core description of the platform should always still present on each
surviving machine. The last machine should then be able to spawn and/or slave
and provision newly available machines and join them in to the network.


Usage
-----
Get the code
```
git clone https://github.com/vdloo/raptiformica; cd raptiformica
```

Make sure you have an SSH agent running
```
eval $(ssh-agent -s); ssh-add
```

Booting a virtualized cluster:
```
export PYTHONPATH=.  

rm -f mutable_config.json  # clean up configs from a previous cluster if there is one
```

```
# Boot a Vagrant (will spawn two dockers in the VM to ensure 3 machines)
./bin/raptiformica_spawn.py --compute-type vagrant --verbose
```

Log in to one of the machines to access the network
```
./bin/raptiformica_members.py
Node           Address               Status  Type    Build  Protocol  DC
fc16:...:fd12  [fc16:...:fd12]:8301  alive   server  0.6.4  2         raptiformica
fc16:...:fa0e  [fc16:...:fa0e]:8301  alive   server  0.6.4  2         raptiformica
fc83:...:6a88  [fc83:...:6a88]:8301  alive   server  0.6.4  2         raptiformica

ssh root@127.0.0.1 -p 2222 -oStrictHostKeyChecking=no

root@archlinux:~# consul exec cat /etc/*release | grep "PRETTY_NAME\|ack"
    fc16:...:fa0e: PRETTY_NAME="Arch Linux"
    fc83:...:6a88: PRETTY_NAME="Ubuntu 16.04.1 LTS"
    fc16:...:fd12: PRETTY_NAME="Ubuntu 16.04.1 LTS"
3 / 3 node(s) completed / acknowledged
```

Development
-----------
```
. activate_venv

# run the tests to check if everything is OK
./runtests.sh -1
```
