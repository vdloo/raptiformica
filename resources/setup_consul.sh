#!/bin/sh
set -e
echo "installing consul service file"
cp /usr/etc/raptiformica/resources/consul.service /etc/systemd/system/multi-user.target.wants/
chmod 664 /etc/systemd/system/multi-user.target.wants/consul.service
