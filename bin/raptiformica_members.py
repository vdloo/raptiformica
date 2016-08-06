#!/usr/bin/env python3
from raptiformica.cli import members

if __name__ == '__main__':
    members()
else:
    raise RuntimeError("This script is an entry point and can not be imported")
