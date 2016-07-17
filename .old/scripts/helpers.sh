#!/usr/bin/bash

# register_check T1 jenkins T1.node.dc1.consul 8089
function register_check() {
    DATA="{\"Datacenter\": \"dc1\", \"Node\": \"$1\", \"Address\": \"$3\", \"Service\": {\"Service\": \"$2\", \"Port\": $4}}"
    echo "Registering $DATA"
    curl -X PUT -d "$DATA" http://127.0.0.1:8500/v1/catalog/register 
}
