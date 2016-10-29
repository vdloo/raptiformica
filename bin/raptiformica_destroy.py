#!/usr/bin/env python3
from raptiformica.cli import destroy

if __name__ == '__main__':
    destroy()
else:
    raise RuntimeError("This script is an entry point and can not be imported")
