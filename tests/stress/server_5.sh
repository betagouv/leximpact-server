#! /usr/bin/env bash

gunicorn --chdir ./$(dirname $0)/../../server app:app --bind 127.0.0.1:5000 --workers=3 --worker-connections=1000 --worker-class=gevent
