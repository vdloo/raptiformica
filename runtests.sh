#!/usr/bin/env bash
set -e

while getopts "1icsrltn" opt; do
    case $opt in
        1) RUN_ONCE=1;;
        i) INTEGRATION=1;;
        # Skip integration tests that boot all nodes at the same time
        c) NO_FULL_CONCURRENT=1;;
        # Skip integration tests that boot all nodes 2 at a time
        s) NO_SEMI_CONCURRENT=1;;
        # Skip integration tests that boot all nodes sequentially
        r) NO_NO_CONCURRENT=1;;
        # Skip integration tests that set up the cluster in a linked formation
        l) NO_LINKED_CLUSTER=1;;
        # Skip integration tests that set up the cluster in a tree formation
        t) NO_TREE_CLUSTER=1;;
        # Skip integration tests that set up the cluster in a normal formation
        n) NO_NORMAL_CLUSTER=1;;
    esac
done

export NO_FULL_CONCURRENT
export NO_SEMI_CONCURRENT
export NO_NO_CONCURRENT
export NO_LINKED_CLUSTER
export NO_TREE_CLUSTER
export NO_NORMAL_CLUSTER

[ -z $INTEGRATION ] && TEST_SUITE="unit" || TEST_SUITE="integration"
[ -z $INTEGRATION ] && TIME_OUT="--process-timeout=30" || TIME_OUT="--process-timeout=2700"

# Do not use the nose.proxy otherwise we can't run Popen with unbuffered output
# fixes: nose.proxy.AttributeError: '_io.StringIO' object has no attribute 'buffer'
[ -z $INTEGRATION ] && NO_CAPTURE="" || NO_CAPTURE="--nocapture"  

shift $((OPTIND - 1))

if [ -z $INTEGRATION ]; then
    if [ -e "/proc/cpuinfo" ]; then
        numprocs=$(cat /proc/cpuinfo  | grep processor | wc -l | cut -d ' ' -f 1)
    elif [ "x$(uname)" = "xDarwin" ]; then
        numprocs=$(sysctl -n hw.ncpu)
    else
        numprocs=1
    fi
else
    echo "Testing sudo so we can start Dockers in the tests"
    sudo echo "Could sudo. Ok!"
    numprocs=1
fi

# Don't write .pyc files
export PYTHONDONTWRITEBYTECODE=1  
# Remove existing .pyc files
find . -type f -name *.pyc -delete

test_cmd="
    echo 'Running raptiformica $TEST_SUITE tests';
    $VIRTUAL_ENV/bin/nosetests --processes=$numprocs tests/$TEST_SUITE $TIME_OUT $NO_CAPTURE;
    echo 'Checking PEP8';
    $VIRTUAL_ENV/bin/autopep8 -r --diff raptiformica;
"

if [ -z $RUN_ONCE ] && [ -z $INTEGRATION ]; then
    LC_NUMERIC="en_US.UTF-8" watch -c -n 0.1 -- "$test_cmd"
else
    sh -ec "$test_cmd"
fi

