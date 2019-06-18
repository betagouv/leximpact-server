#! /usr/bin/env bash

ab -p ./$(dirname $0)/payload.json -T application/json -n 1000 -c 10 http://127.0.0.1:5000/calculate/compare
