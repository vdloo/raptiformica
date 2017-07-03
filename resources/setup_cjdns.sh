#!/bin/sh
set -e
echo "changing directory to /usr/etc/cjdns"
cd /usr/etc/cjdns

echo "Checking for a pre-compiled cjdroute"

echo "ensuring binary is compiled"
if [ ! -f cjdroute ]; then
    if [ -f ~/.raptiformica.d/artifacts/$(uname -m)/cjdns/cjdroute ]; then
        echo 'using stored artifact'
        cp ~/.raptiformica.d/artifacts/$(uname -m)/cjdns/cjdroute .
    else
        echo 'compiling new cjdoute'
        lsb_release -a 2>&1 | grep Raspbian -i -q && Seccomp_NO=1 ./do || ./do
        mkdir -p ~/.raptiformica.d/artifacts/$(uname -m)/cjdns/
        cp -f cjdroute ~/.raptiformica.d/artifacts/$(uname -m)/cjdns/
    fi
fi

echo "ensuring tun device exists"
if cat /dev/net/tun | grep -q "File descriptor in bad state" ; then
    mkdir -p /dev/net && mknod /dev/net/tun c 10 200 && chmod 0666 /dev/net/tun
fi

if cat /dev/net/tun | grep -q "File descriptor in bad state" ; then
    echo "couldn't configure tun device"
    exit 1
else
    echo "ensuring cjdroute.conf"
    umask 077 && ./cjdroute --genconf | ./cjdroute --cleanconf > cjdroute.conf
fi

echo "ensuring binary and config to /usr/bin"
cp -f cjdroute /usr/bin/
if [ ! -f /etc/cjdroute.conf ]; then
    cp cjdroute.conf /etc/
fi

