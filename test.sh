#!/usr/bin/env bash

# Get args
if [ -z $1 ]; then
    arg=""
else
    arg='--app '$1
fi


if [ ! -d venv ]; then
    echo 'install before testing'
    exit
fi

if [[ "$VIRTUAL_ENV" == "" ]]; then
    source venv/bin/activate
fi

flake8 probemanager/$1 --config=.flake8


coverage erase
coverage run --source=probemanager/$1 probemanager/runtests.py $arg
coverage report -i --skip-covered
coverage html
