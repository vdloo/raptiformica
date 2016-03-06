#!/usr/bin/bash
set -e
echo "ensuring dependencies are installed"
type -p pacman 1> /dev/null && pacman -S --noconfirm nodejs base-devel --needed
type -p apt-get 1> /dev/null && (apt-get update -yy && apt-get install -yy nodejs build-essential git python)
echo "ensuring cjdns repo is cloned"
[ ! -d cjdns ] && git clone https://github.com/cjdelisle/cjdns.git cjdns
cd cjdns
#echo "ensuring version 17.1 is checked out"
#git checkout cjdns-v17.1
echo "ensuring binary is compiled"
[ ! -f cjdroute ] && ./do
echo "ensuring tun device exists"
if cat /dev/net/tun | grep -q "File descriptor in bad state" ; then
    mkdir -p /dev/net && mknod /dev/net/tun c 10 200 && chmod 0666 /dev/net/tun
fi

if cat /dev/net/tun | grep -q "File descriptor in bad state" ; then
    echo "couldn't configure tun device"
else
    echo "ensuring cjdroute.conf"
    [ ! -f cjdroute.conf ] &&(umask 077 && ./cjdroute --genconf > cjdroute.conf)
fi
#if ! grep -q "s1.rickvandeloo.com" cjdroute.conf; then
#    sed -i '/ipv4 address:port/i\\t\t\t\t\t"example.com:64073": {"login": "default-login", "password": "secret", "publicKey": "secret", "peerName": "secret"}' /etc/cjdroute.conf
#fi

echo "ensuring binary and config to /usr/bin"
cp cjdroute /usr/bin/
cp cjdroute.conf /etc/

echo "installing cjdns service file"
cp ../cjdns.service /etc/systemd/system/multi-user.target.wants/
chmod 664 /etc/systemd/system/multi-user.target.wants/cjdns.service

echo "Rebooting to ensure the tun module is loaded into the kernel after upgrade"
type -p pacman 1> /dev/null && (sleep 5; reboot) & exit
