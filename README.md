Raptiformica
============

Decentralized server orchestration

## What is this?

This is a tool for clustering servers to host services in a completely
decentralized fashion. Raptiformica works by creating a decentralized
overlay mesh network using CJDNS and running Consul to use distributed
consensus to connect new peers to all other peers in the network.

It allows you to cluster servers in different zones or behind firewalls,
and even mobile devices, as if they were in one network even when network
connections and routes change.

For example: if you cluster an Android phone and you switch from wifi
to LTE, you will be able to resume your SSH connection the machine after
a short freeze of the shell as the network will automatically find a path
back to the machine.

For an example of what can be built with this, check out these slides about
[hosting high available websites on mobile phones](https://nbviewer.jupyter.org/format/slides/github/vdloo/slides/blob/master/decentralized_server_orchestration/presentation.ipynb)


Usage
-----
Get the code
```sh
git clone https://github.com/vdloo/raptiformica; cd raptiformica

# System wide installation (optional)
make install
```


Make sure you have an SSH agent running
```sh
eval $(ssh-agent -s); ssh-add
```

Booting an example cluster of Dockers:

```sh
# Spawn 3 Dockers
raptiformica spawn --compute-type docker --verbose
raptiformica spawn --compute-type docker --verbose
raptiformica spawn --compute-type docker --verbose

# Check out the consul members of the spawned cluster
raptiformica members
Node           Address               Status  Type    Build  Protocol  DC
fc16:...:fd12  [fc16:...:fd12]:8301  alive   server  0.6.4  2         raptiformica
fc16:...:fa0e  [fc16:...:fa0e]:8301  alive   server  0.6.4  2         raptiformica
fc83:...:6a88  [fc83:...:6a88]:8301  alive   server  0.6.4  2         raptiformica
```

Log in to one of the machines to access the network
```sh
# SSH into the first available machine
raptiformica ssh

# Note the created `tun0` interface
ip addr

# You can SSH to any of the other machines using the address found in the consul
# members list. As a test, you can firewall the Docker IPv4 address of one of the
# other Dockers on one of the machines. You should still be able to directly SSH
# into the firewalled machine because CJDNS will route through the still available
# path via the third Docker.
ssh root@[fc83:...:6a88]
```

## How does it work?

When you slave a machine with raptiformica it will create a TUN device
using CJDNS and generate an IPv6 address for the slaved host. Then it will
install consul and check if there are already enough other hosts available
to form consensus. When three hosts have been slaved, consensus is formed
and information about all peers in the network will be shared among the
members of the network so the network can gracefully scale and shrink with
newly available servers and servers changing network connections, going down
or leaving the cluster.

When a new server joins the mesh all other peers are updated with connection
details to the new machine, and as long as there is at least one route to each
machine all machines can directly connect to each other using a pre-generated
IPv6 address. This is possible because CJDNS implements DHT routing at the
packet level. From the perspective of the Linux machine there is just a
network interface with an IPv6 address through which packets can be sent.
How they end up at the destination by being passed through other nodes is
completely abstracted away by the mesh networking software.

By creating this decentralized virtual network it is possible to pretend
scattered devices are actually in one network even if they are quickly
changing network configurations (like mobile phones moving in and out of wifi),
removing all the complexity of having to manage machines in different zones and
behind firewalls. The meshnet just routes around it transparently and the IP
address of each machine stays the same regardless of the location of the machine
in relation to other machines.

## Applications

The use case for this project is creating a resilient cluster platform where
there should be no single point of failure, the hardware is not in a homogeneous
location like a datacenter and it does not matter if the nodes are mobile.

This enables you to run datacenter applications on and easily create resilient
beowulf clusters of servers in different zones and behind firewalls, and mobile
devices like laptops and mobile phones.

This can be desirable when:

- You want to run a cloud cluster across multiple datacenter zones
- You want to run a cloud cluster across multiple cloud providers
- You want to create a cluster of mobile phones or other mobile devices
- You want to cluster nodes behind a NAT or another firewall (only needs outbound UDP)
- You want to avoid a single point of failure in a cluster platform
- You want to build a cluster platform that's completely self healing
- You want to build a cluster platform that can auto scale
- You want to create completely decentralized self-hosted applications

The trade off:
- The mesh routing is requires quite some CPU depending on the traffic
- Does not scale well beyond 25 servers at this moment (depends on the hardware and stability of your nodes)
- All nodes are Consul masters, there are no clients
- Currently very experimental and unstable. API will change a lot.

## Principles

There are a couple of fundamentals on which this project is based.

### The decentralized network

Any machine can join the network as long as at least one other machine in
the network can reach it. This allows for the creation of a virtual
data center using scattered resources. When moving machines can participate 
in the network (laptops, rooted Androids running Linux), available computing
power can be leveraged which otherwise might be difficult due to networking
and routing.

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

### No dependencies

At least in the bootstrapping part of the application. Only a python
3 interpreter and a checkout of raptiformica should be enough to run the
core code. This way it is enough to only rsync the code of an instance to 
a new machine in order to get things running. It is OK to have dependencies
in plugins or processes interfacing with the raptiformica APIs. 

### No provisioning logic in the core code

Provisioning scripts should be configured as `server_type` modules. 
See `modules/server_types/base.json` for an example. By implementing the
provisioning logic outside of the application it does not matter if
Ansible, Puppet or something else is used, as long as there is a repository 
to check out and a command to run to start the provisioning process on the 
machine.

This keeps raptiformica extensible with modules while the core only takes
care of establishing the network. Adding too many modules to the core code
could make the network creation and maintaining code slow or unstable. But
it is possible to augment the core code with your own provisioning scripts
and that in some cases has some advantages.

But if you don't strictly need that, I suggest just doing your provisioning
after the network has been established unless you have a good reason why to
hook it into the core mesh networking services provisioning.

### No compute logic in the core code

It is possible to create a raptiformica plugin for a new instance provider.
This can be anything as long as it returns an IP address on which can be
logged in as root to join the machine into the decentralized network.

Logic for starting an instance should be configured as `compute_type`
modules just like `server_types`. See `default_docker_compute_type.json`
and `docker_compute_type.json`. A `compute_type` is implemented by 
configuring a `start_instance_command`, `get_hostname_command` and 
`get_port_command`.

See `raptiformica/modules/compute` for an example of a compute provider.
All internal providers are also implemented as a plugin.

## Related projects

There are a couple of other projects that relate to raptiformica. Some
are used by raptiformica, others use raptiformica. For the bigger picture
of what this all entails I figured I'd compile as short list here.

#### [raptiformica-map](https://github.com/vdloo/raptiformica-map)

A completely decentralized web service visualizing the nodes in a
raptiformica cluster. Uses the consul distributed key value store
provisioned by raptiformica to store it's data. Nodes compile and
run a h2o reverse proxy to proxy through the meshnet using DNSmasq
and the consul DNS server to self-registered Flask webservers
serving a javascript map of the network based on reported edges
to their neighbours from each node.

Can be installed with
```sh
raptiformica install vdloo/raptiformica-map
```

#### [consul-kv](https://github.com/vdloo/consul-kv)

A Python 3 client for the Consul key value database. This is used
by raptiformica to write and retrieve data about peers and the
cluster config from the collective memory of all nodes.

#### [jobrunner](https://github.com/vdloo/jobrunner)

Example of a decentralized job processing system that can run 
on top of raptiformica. This could allow the network to distribute 
work across nodes and keep a persistent record of state of a process 
so that at the moment a node loses connection to the cluster another 
can continue the work where the other node left of, or reschedule a 
service to the next available machine based on certain criteria.

### [raptiformica-docker-32-bit](https://github.com/vdloo/raptiformica-docker-32bit)

Raptiformica plugin that adds a new compute type: a 32 bit version of the
default raptiformica docker provider. It is exactly the same except that it
uses a 32 bit Docker base to layer the phusion baseimage-docker provisioning
over and builds the raptiformica docker based on that baseimage. I've still
got an i686 running somewhere and it was nice to get this to run on that as well.

Can be installed with
```sh
raptiformica install vdloo/raptiformica-docker-32bit
```

#### [android-x86-64-vagrant](https://github.com/vdloo/android-x86-64-vagrant)

Can be used to simulate a cluster of mobile phones. A collection
of script that imports an android-x86 ISO and uses packer to send
keystrokes in order to install Linuxdeploy and install an Archlinux
chroot in the Android VM and start an SSH server. At that point the
machine will be packaged as a Vagrant box. The created Vagrant box
is then an accurate simulation of a rooted Android phone with an
Archlinux chroot that might be slaved by raptiformica in order to
form a cluster of mobile phones. Note that this is an x86 VM, not
ARM. So take not that on real mobile phones you might need to compile
your software for ARM for it to work.

#### [vagrant-tun](https://github.com/vdloo/vagrant-tun)

A Vagrant plugin that makes sure there is a TUN/TAP device available in
a usable state. This is used by the default Vagrant compute type
in raptiformica. It can be installed with `vagrant plugin install vagrant-tun`.

Basically it runs the following as soon as there is SSH connectivity:

```bash
mkdir -p /dev/net && mknod /dev/net/tun c 10 200 && chmod 0666 /dev/net/tun
```

Additionally, if it needs to reboot because provisioning installed a newer
kernel or headers than fit the tun module that is currently loaded into the
kernel, it will reboot the machine before continuing.


#### [puppetfiles](https://github.com/vdloo/puppetfiles)

A repository with puppet recipes and a raptiformica module definition.
This repository can serve as an example of how to implement custom
raptiformica server types. Custom server types will show up when you
run ```raptiformica slave --help``` under the `--server-type` option.

Can be installed with
```sh
raptiformica install vdloo/puppetfiles
```

Heavily customized server types are not recommended because they might
interfere with the cluster creation provisioning. Also these hooks might
fire very often in case of many cluster changes, which might be
computationally heavy and only detrimental to cluster health.


#### [raptiformica-notify-kodi](https://github.com/vdloo/raptiformica-notify-kodi)

Quick and dirty raptiformica plugin that hooks into some internal
events and sends a notification to Kodi using [kodictl](https://github.com/vdloo/kodictl).
The shell script is pretty much garbage and it requires that you have
racket and kodictl installed, but it might serve as an example of how
to configure a plugin that hooks into these core events by creating a
`raptiformica.json` file in your project root that specifies a `platform`
configuration. Listens to `cluster_change`, `after_start_instance`,
`after_slave`, `after_assimilate` and `after_mesh`.

Development
-----------
```
. activate_venv

# run the tests to check if everything is OK
./runtests.sh -1
```
