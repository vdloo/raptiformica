#!/bin/sh
set -e
echo "changing directory to /usr/etc/cjdns"
cd /usr/etc/cjdns

echo "ensuring binary is compiled"
[ ! -f cjdroute ] && ./do

echo "ensuring tun device exists"
if cat /dev/net/tun | grep -q "File descriptor in bad state" ; then
    mkdir -p /dev/net && mknod /dev/net/tun c 10 200 && chmod 0666 /dev/net/tun
fi

if cat /dev/net/tun | grep -q "File descriptor in bad state" ; then
    echo "couldn't configure tun device"
    exit 1
else
    echo "ensuring cjdroute.conf"
    [ ! -f cjdroute.conf ] && (umask 077 && ./cjdroute --genconf > cjdroute.conf)
fi

echo "ensuring binary and config to /usr/bin"
cp cjdroute /usr/bin/
cp cjdroute.conf /etc/

echo "installing cjdns service file"
cp /usr/etc/raptiformica/resources/cjdns.service /etc/systemd/system/multi-user.target.wants/
chmod 664 /etc/systemd/system/multi-user.target.wants/cjdns.service
