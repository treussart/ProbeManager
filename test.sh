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

venv/bin/flake8 probemanager/$1 --config=.flake8


venv/bin/coverage erase
venv/bin/coverage run --source=probemanager/$1 probemanager/runtests.py $arg
venv/bin/coverage report -i --skip-covered
venv/bin/coverage html

if [ -f .coveralls.yml ]; then
    echo "Send data to Coveralls ?, y/N followed by [ENTER]:"
    read answer
    if [ ! -z $answer ]; then
        if [ $answer == 'y' ]; then
            venv/bin/coveralls
        fi
    fi
fi
