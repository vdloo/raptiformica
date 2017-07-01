[![Build Status](https://travis-ci.org/vdloo/consul-kv.svg?branch=master)](https://travis-ci.org/vdloo/consul-kv)

# consul-kv

Python 3 client for the [consul key/value store](https://www.consul.io/docs/agent/http/kv.html).

## Installation

Get it from [pypi](https://pypi.python.org/pypi/consul_kv/)
```
pip install consul_kv
```

Or install directly from GitHub
```
pip install git+https://github.com/vdloo/consul-kv.git@master#egg=consul_kv
```

## Usage

Instantiate a client
```python
from consul_kv import Connection
conn = Connection(endpoint='http://localhost:8500/v1/kv')
```

PUT a key
```python
conn.put('the/key', 'the_value')
```

Atomically PUT a list of keys and values ([transaction](https://www.consul.io/docs/agent/http/kv.html#txn)).
```python
mapping = {
    'a/key': 'a_value',
    'another/k': 'another_value'
}
conn.put_mapping(mapping)
```

Atomically PUT a dictionary
```python
dictionary = {
    'a': {
        'key': 'a_value'
    },
    'another': {
        'k': 'another_value'
    }
}
conn.put_dict(dictionary)
```

GET a key
```python
conn.get('the/key')
{'the/key': 'the_value'}
```

GET all keys under a path
```python
conn.get('the', recurse=True)
{'the/key': 'the_value', 'the/other_key': 'the_other_value'}

# or
conn.get_mapping('the')
{'the/key': 'the_value', 'the/other_key': 'the_other_value'}
```

GET a dictionary based on all keys under a path
```python
conn.get_dict('the')
{'the': {'key': 'the_value', 'other_key': 'the_other_value'}}
```

DELETE a key
```python
conn.delete('the/key')
```

DELETE all keys under a path
```python
conn.delete('the', recurse=True)
```


## Development

Create a virtualenv
```
mkvirtualenv -a $(pwd) -p /usr/bin/python3 consul_kv
echo "PYTHONPATH=`pwd`" >> $VIRTUAL_ENV/bin/postactivate
pip3 install pip --upgrade
pip3 install -r requirements/development.txt
```

Run the tests
```
./runtests.sh -1
```
