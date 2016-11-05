#!/usr/bin/env sh
pacman -Sy --noconfirm
pacman -S ruby git puppet --noconfirm
pacman -S acl --noconfirm

# Make sure the kernel is not upgraded on 'pacman -Syu' because otherwise we'd need to reboot
# yet again before docker will work inside the virtualized guest due to the right veth kernel module 
# not being able to be loaded.  Workaround for:
# docker: Error response from daemon: failed to create endpoint ... on network bridge: 
# failed to add the host (...) <=> sandbox (...) pair interfaces: operation not supported.
grep -q "IgnorePkg = linux" "/etc/pacman.conf" || sed -i '/\[options\]/a IgnorePkg = linux' /etc/pacman.conf 
