Raptiformica
============

A self healing distributed infrastructure

Usage
-----
Get the code
```
# create a checkout
git clone https://github.com/vdloo/raptiformica; cd raptiformica
```

Make sure you have an SSH agent running
```
eval $(ssh-agent -s); ssh-add
```

Booting a Docker cluster:
```
rm -f mutable_config.json  # clean up configs from a previous cluster if there is one
export PYTHONPATH=.  # You need at least 3 instances to establish the distributed network
for i in {1..3}; do ./bin/raptiformica_spawn.py --compute-type docker --no-provision; done
```

Log in to one of the machines to access the network
```
./bin/raptiformica_members.py
Node           Address               Status  Type    Build  Protocol  DC
fc16:...:fd12  [fc16:...:fd12]:8301  alive   server  0.6.4  2         raptiformica
fc16:...:fa0e  [fc16:...:fa0e]:8301  alive   server  0.6.4  2         raptiformica
fc83:...:6a88  [fc83:...:6a88]:8301  alive   server  0.6.4  2         raptiformica

ssh root@172.17.0.3 -oStrictHostKeyChecking=no
root@19097ae40f0e:~# consul exec echo hello world | grep "hello\|ack"
    fc16:...:fa0e: hello world
    fc83:...:6a88: hello world
    fc16:...:fd12: hello world
3 / 3 node(s) completed / acknowledged
```

Development
-----------
```
# create a checkout
git clone https://github.com/vdloo/raptiformica; cd raptiformica

. activate_venv

# run the tests to check if everything is OK
./runtests.sh -1
```
