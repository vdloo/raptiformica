#!/usr/bin/env sh
# Don't use the default mirrors for the initial upgrade
echo -e 'Server = http://mirror.nl.leaseweb.net/archlinux/$repo/os/$arch\nServer = http://ftp.snt.utwente.nl/pub/os/linux/archlinux/$repo/os/$arch' > /etc/pacman.d/mirrorlist

pacman -Sy archlinux-keyring --noconfirm --needed
pacman -Sy --noconfirm
pacman -S ruby git puppet --noconfirm --needed
pacman -S acl --noconfirm --needed

# Make sure the kernel is not upgraded on 'pacman -Syu' because otherwise we'd need to reboot
# yet again before docker will work inside the virtualized guest due to the right veth kernel module 
# not being able to be loaded.  Workaround for:
# docker: Error response from daemon: failed to create endpoint ... on network bridge: 
# failed to add the host (...) <=> sandbox (...) pair interfaces: operation not supported.
grep -q "IgnorePkg = linux" "/etc/pacman.conf" || sed -i '/\[options\]/a IgnorePkg = linux' /etc/pacman.conf 
