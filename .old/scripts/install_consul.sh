#!/usr/bin/bash
set -e
echo "changing directory to /usr/etc/consul"
cd /usr/etc/consul
echo "ensuring dependencies are installed"
type -p apt-get 1> /dev/null && (apt-get install -yy wget unzip)

wget https://releases.hashicorp.com/consul/0.6.3/consul_0.6.3_linux_amd64.zip
unzip consul_0.6.3_linux_amd64.zip
mv consul /usr/bin/consul

mkdir -p /etc/consul.d
mkdir -p /opt/consul
echo -e "{\n  \"data_dir\": \"/opt/consul\",\n  \"datacenter\": \"cjdns\",\n  \"node_name\": \"$HOSTNAME\",\n  \"server\": false,\n  \"bind_addr\": \"::\",\n  \"advertise_addr\": \"$(ip addr | grep tun -A 2 | grep inet6 | awk '{print$2}' | cut -d '/' -f1)\",\n  \"encrypt\": \"h1mxc5mqPb+zR6jD/hnrJg==\"\n}" > /etc/consul.d/config.json
(sleep 5; consul join [fce6:de42:a89:9765:a752:5d3c:3c27:4c07]:8301 [fc1d:308f:17b1:8eea:a371:ff35:39c2:a3b3]:8301 [fcf7:582:63b8:daf6:e3fa:720:9514:286b]:8301)& 
(consul agent --config-dir /etc/consul.d)&
