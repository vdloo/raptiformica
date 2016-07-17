#!/usr/bin/env bash
set -e

while getopts "1" opt; do
    case $opt in
        1) RUN_ONCE=1;;
    esac
done

shift $((OPTIND - 1))

if [ -e "/proc/cpuinfo" ]; then
    numprocs=$(cat /proc/cpuinfo  | grep processor | wc -l | cut -d ' ' -f 1)
elif [ "x$(uname)" = "xDarwin" ]; then
    numprocs=$(sysctl -n hw.ncpu)
else
    numprocs=1
fi

# Don't write .pyc files
export PYTHONDONTWRITEBYTECODE=1  
# Remove existing .pyc files
find . -type f -name *.pyc -delete

test_cmd="
    echo 'Running raptiformica unit tests';
    nosetests --processes=$numprocs;
    echo 'Checking PEP8';
    autopep8 -r --diff raptiformica;
"

if [ -z $RUN_ONCE ]; then
    LC_NUMERIC="en_US.UTF-8" watch -c -n 0.1 -- "$test_cmd"
else
    sh -ec "$test_cmd"
fi
