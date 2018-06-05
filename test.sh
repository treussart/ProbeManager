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
    export DJANGO_SETTINGS_MODULE="probemanager.settings.dev"
    LOG_PATH="/var/log/"
    TRAVIS_JOB_NUM_MIN=$( echo $TRAVIS_JOB_NUMBER | cut -f2 -d '.' )
else
    export DJANGO_SETTINGS_MODULE="probemanager.settings.dev"
    LOG_PATH="probemanager/"
fi

# test if fixtures secrets files are here
if [ ! -f probemanager/core/fixtures/test-core-secrets.json ]; then
    echo 'Secrets fixtures not found'
    exit 1
fi
FAIL_UNDER="90"
flake8 $source --config=.flake8
result_flake8="$?"
if [ "$result_flake8" -ne 0 ]; then
    echo "Tests failed : PEP-8 Not Compliant"
    exit "$result_flake8"
fi
coverage erase
coverage run $sourcecoverage probemanager/runtests.py $arg
result_run="$?"
if [ "$result_run" -ne 0 ]; then
    echo "Tests failed"
    exit "$result_run"
fi
coverage report --fail-under="$FAIL_UNDER"
result_report="$?"
coverage html --skip-covered
if [ "$result_report" -ne 0 ]; then
    echo "Tests failed : Coverage under $FAIL_UNDER %"
    exit "$result_report"
fi

if [[ "$CODACY_PROJECT_TOKEN" != "" && "$TRAVIS_JOB_NUM_MIN" = "1" ]]; then
    coverage xml
    python-codacy-coverage -r coverage.xml

    coverage xml -o coverage-suricata.xml --include='probemanager/suricata/*'
    python probemanager/scripts/remove_in_file.py -p probemanager/suricata/ -p probemanager.suricata -r ProbeManager:ProbeManager/probemanager/suricata -f coverage-suricata.xml
    ( cd probemanager/suricata && python-codacy-coverage -r ../../coverage-suricata.xml -t $CODACY_SURICATA_TOKEN )

    coverage xml -o coverage-checkcve.xml --include='probemanager/checkcve/*'
    python probemanager/scripts/remove_in_file.py -p probemanager/checkcve/ -p probemanager.checkcve -r ProbeManager:ProbeManager/probemanager/checkcve -f coverage-checkcve.xml
    ( cd probemanager/checkcve && python-codacy-coverage -r ../../coverage-checkcve.xml -t $CODACY_CHECKCVE_TOKEN )

    coverage xml -o coverage-bro.xml --include='probemanager/bro/*'
    python probemanager/scripts/remove_in_file.py -p probemanager/bro/ -p probemanager.bro -r ProbeManager:ProbeManager/probemanager/bro -f coverage-bro.xml
    ( cd probemanager/bro && python-codacy-coverage -r ../../coverage-bro.xml -t $CODACY_BRO_TOKEN )
fi
if [[ -f "$LOG_PATH"probemanager-error.log && "$TRAVIS" = true ]]; then
    echo "#### ERROR LOGS ####"
    cat "$LOG_PATH"probemanager-error.log
fi
if [[ -f "$LOG_PATH"probemanager-celery.log && "$TRAVIS" = true ]]; then
    echo "#### CELERY LOGS ####"
    cat "$LOG_PATH"probemanager-celery.log
fi

exit
