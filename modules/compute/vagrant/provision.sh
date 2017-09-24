#!/usr/bin/env sh
userdel terry --force || /bin/true  # remove image maintainer's user

# make sure the keys from the ssh agent can log in as root
mkdir -p /root/.ssh/
touch /root/.ssh/authorized_keys
if ssh-add -L >/dev/null 2>/dev/null; then
    auth_keys_file='/root/.ssh/authorized_keys'
    agent_keys=$(ssh-add -L | awk '!NF || !seen[$0]++' "$auth_keys_file" -)
    echo "$agent_keys" > "$auth_keys_file"
fi
