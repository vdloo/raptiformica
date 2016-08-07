#!/usr/bin/env python3
from raptiformica.cli import prune

if __name__ == '__main__':
    prune()
else:
    raise RuntimeError("This script is an entry point and can not be imported")
