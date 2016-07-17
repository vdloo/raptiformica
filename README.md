Raptiformica
============

A self healing distributed infrastructure

Named after the formica sanguinea, an ant species of slave-makers that can
become self sufficient when necessary. These blood-red ants are also
haplometrotic, meaning an entire new colony can be founded by a single
fertilized, egg laying queen.

### Development

Make a virtualenv and get a recent pip
```
mkvirtualenv -a $(pwd) -p /usr/bin/python3 raptiformica
echo "PYTHONPATH=`pwd`" >> $VIRTUAL_ENV/bin/postactivate
pip3 install pip --upgrade
pip3 install -r requirements/base.txt
```


