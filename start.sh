#!/usr/bin/env bash

if [ -z $1 ] || [ $1 == 'dev' ]; then
    arg="dev"
elif [ $1 == 'prod' ]; then
    arg=$1
else
    echo 'Bad argument'
    exit 1
fi

if [[ "$VIRTUAL_ENV" == "" ]]; then
    if [ ! -d venv ]; then
        echo 'install before starting the server'
        exit
    else
        source venv/bin/activate
    fi
fi

if [ ! -f probemanager/celery.pid ]; then
    (cd probemanager/ && ../venv/bin/celery -A probemanager worker -D --pidfile celery.pid -B -l debug -f celery.log --scheduler django_celery_beat.schedulers:DatabaseScheduler)
else
    kill $( cat probemanager/celery.pid)
    sleep 3
    pkill -f celery
    sleep 3
    (cd probemanager/ && ../venv/bin/celery -A probemanager worker -D --pidfile celery.pid -B -l debug -f celery.log --scheduler django_celery_beat.schedulers:DatabaseScheduler)
fi

venv/bin/python probemanager/manage.py runserver --settings=probemanager.settings.$arg
