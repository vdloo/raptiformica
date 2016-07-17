#!/usr/bin/bash
set -e 
if ! grep -q "s1.rickvandeloo.com" /etc/cjdroute.conf; then
    sed -i '/ipv4 address:port/i\\t\t\t\t\t"s1.rickvandeloo.com:64073": {"login": "fsociety", "password": "4977g9np2y5gf2rcgvgcqthfy3zqn50", "publicKey": "pnjf5k59tjnm2ps5u4xl7j9fz915pcxz1dvsh62yncuqmddlv0u0.k", "peerName": "fsociety"}' /etc/cjdroute.conf
fi
type -p apt-get 1> /dev/null && /usr/bin/cjdroute < /etc/cjdroute.conf
