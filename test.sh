#!/usr/bin/env bash

# Get args
if [ -z $1 ]; then
    arg=""
else
    arg='--app '$@
fi
source=''
sourcecoverage=''
for app in $@
do
    source="$source"" probemanager/""$app"
    sourcecoverage="$sourcecoverage""probemanager/""$app"","
done
sourcecoverage="--source=""$sourcecoverage"

if [[ "$VIRTUAL_ENV" = "" ]]; then
    if [ ! -d venv ]; then
        echo 'Install before testing'
        exit
    else
        source venv/bin/activate
    fi
fi

if [[ "$TRAVIS" = true ]]; then
    export DJANGO_SETTINGS_MODULE="probemanager.settings.prod"
    LOG_PATH="/var/log/"
else
    export DJANGO_SETTINGS_MODULE="probemanager.settings.dev"
    LOG_PATH="probemanager/"
fi

# test if fixtures secrets files are here
if [ ! -f probemanager/core/fixtures/test-core-secrets.json ]; then
    echo 'Secrets fixtures not found'
    exit 1
fi
flake8 $source --config=.flake8
coverage erase
coverage run $sourcecoverage probemanager/runtests.py $arg
coverage report
coverage html --skip-covered

if [[ "$CODACY_PROJECT_TOKEN" != "" ]]; then
    coverage xml
    python-codacy-coverage -r coverage.xml

    coverage xml -o coverage-suricata.xml --include='probemanager/suricata/*'
    python probemanager/scripts/remove_in_file.py -p probemanager/suricata/ -p probemanager.suricata. -p probemanager.suricata -f coverage-suricata.xml
    python-codacy-coverage -d probemanager/suricata -r coverage-suricata.xml -t $CODACY_SURICATA_TOKEN

    coverage xml -o coverage-checkcve.xml --include='probemanager/checkcve/*'
    python probemanager/scripts/remove_in_file.py -p probemanager/checkcve/ -p probemanager.checkcve. -p probemanager.checkcve -f coverage-checkcve.xml
    python-codacy-coverage -d probemanager/checkcve -r coverage-checkcve.xml -t $CODACY_CHECKCVE_TOKEN
fi
if [ -f .coveralls.yml ]; then
    coveralls
fi
if [ -f "$LOG_PATH"probemanager-error.log ]; then
    echo "#### ERROR LOGS ####"
    cat "$LOG_PATH"probemanager-error.log
fi
if [ -f "$LOG_PATH"probemanager-celery.log ]; then
    echo "#### CELERY LOGS ####"
    cat "$LOG_PATH"probemanager-celery.log
fi

exit
