#!/usr/bin/env python3
from raptiformica.cli import slave

if __name__ == '__main__':
    slave()
else:
    raise RuntimeError("This script is an entry point and can not be imported")
