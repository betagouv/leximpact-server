#! /usr/bin/env bash

curl -d "@./$(dirname $0)/payload.json" -H "Content-Type: application/json" http://localhost:5000/calculate/compare
