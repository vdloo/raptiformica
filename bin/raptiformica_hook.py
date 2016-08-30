#!/usr/bin/env python3
from raptiformica.cli import hook

if __name__ == '__main__':
    hook()
else:
    raise RuntimeError("This script is an entry point and can not be imported")
