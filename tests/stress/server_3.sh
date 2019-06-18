#! /usr/bin/env bash

gunicorn --chdir ./$(dirname $0)/../../server app:app --bind 127.0.0.1:5000 --keep-alive 30 --workers=9 --worker-class=meinheld.gmeinheld.MeinheldWorker
