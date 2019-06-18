#! /usr/bin/env bash

FLASK_ENV=production HOST=127.0.0.1 PORT=5000 python ./$(dirname $0)/../../server/app.py
