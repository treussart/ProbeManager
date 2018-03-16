#!/usr/bin/env bash

HELP="
First argument : dev or prod
Second argument : path to the install destination (Only with prod argument)
dev : For local devlopement.
prod : For use in production.
Example :
./install.sh dev
./install.sh prod /usr/local/share
"

# Get args
if [ -z $1 ] || [ $1 == 'dev' ]; then
    arg="dev"
    dest=""
elif [ $1 == 'prod' ]; then
    arg=$1
    if [ -z $2 ]; then
        dest='/usr/local/share'
    else
        dest=$2
    fi
elif [ $1 == 'help' ]; then
    echo "$HELP"
    exit
else
    echo 'Bad argument'
    exit 1
fi
destfull="$dest"/ProbeManager/

install_modules(){
    echo '## Install the modules ##'
    for f in probemanager/*; do
        if [[ -d $f ]]; then
            if test -f "$f"/install.sh ; then
                ./"$f"/install.sh $arg $destfull
            fi
        fi
    done
}

clean() {
    echo '## Clean Files ##'
    if [ $arg == 'dev' ]; then
        if [ ! -d venv ]; then # First install in dev mode - for init to develop branch
            git checkout develop
            git submodule foreach --recursive git checkout develop
        fi
    fi
    if [ -f conf.ini ]; then
        rm conf.ini
    fi
    for f in probemanager/*; do
        if [[ -d $f ]]; then
            if test -d "$f"/migrations ; then
                rm "$f"/migrations/00*.py
            fi
        fi
    done
    if [ -f probemanager/celerybeat-schedule.db ]; then
        rm probemanager/celerybeat-schedule.db
    fi
    if [ -f probemanager/probemanager.log ]; then
        rm probemanager/probemanager.log
    fi
    if [ -f probemanager/celery.log ]; then
        rm probemanager/celery.log
    fi
    if [ -f .coverage ]; then
        rm .coverage
    fi
}

copy_files(){
    echo '## Copy files in install dir ##'
    if [ -d $2 ]; then
        # copy the project
        cp -r probemanager $destfull
        # copy the doc
        cp -r docs $destfull
        # copy the start script for test
        cp start.sh $destfull
        cp README.rst $destfull
    fi
}

installOsDependencies() {
    echo '## Install Dependencies ##'
    # Debian
    if [ -f /etc/debian_version ]; then
        grep -v "#" requirements/os/debian.txt | grep -v "^$" | sudo xargs apt install -y
        if [ $arg == 'prod' ]; then
            grep -v "#" requirements/os/debian_prod.txt | grep -v "^$" | xargs apt install -y
        fi
    fi
    # OSX with brew
    if [[ $OSTYPE == *"darwin"* ]]; then
        if brew --version | grep -qw Homebrew ; then
            grep -v "#" requirements/os/osx.txt | grep -v "^$" | xargs brew install
            if [ $arg == 'prod' ]; then
                grep -v "#" requirements/os/osx_prod.txt | grep -v "^$" | xargs brew install
            fi
        fi
    fi
}

chooseApps(){
    echo '## Choose Apps ##'
    i=0
    for f in probemanager/*; do
        if [[ -d $f ]]; then
            if [[  -f "$f"/install.sh ]] || [[  -f "$f"/init_db.sh ]] ; then
                apps[i]=$( echo $f | cut -f2 -d"/" )
                i=$((i+1))
            fi
        fi
    done
    for i in ${apps[@]}; do
        if [[ -z "${text// }" ]];then
            text=$text"'"$i"'"
        else
            text=$text", '"$i"'"
        fi
    done
    echo "Module(s) available : "${apps[*]}
    echo "[APPS]" >> "$destfull"conf.ini
    echo "PROD_APPS = ["$text"]" >> "$destfull"conf.ini
}

setGit(){
    echo '## Set Git ##'
    git_bin=$( which git )
    if [ $arg == 'prod' ]; then
        echo "[GIT]" >> "$destfull"conf.ini
        echo "GIT_BINARY = $git_bin" >> "$destfull"conf.ini
    else
        echo "[GIT]"  >> conf.ini
        echo "GIT_BINARY = $git_bin" >> conf.ini
    fi
}

installVirtualEnv() {
    echo '## Create Virtualenv ##'
    if [ $arg == 'prod' ]; then
        if [ ! -d "$destfull"venv ]; then
            python3 -m venv "$destfull"venv
            source "$destfull"venv/bin/activate
            "$destfull"venv/bin/pip3 install wheel
            "$destfull"venv/bin/pip3 install -r requirements/prod.txt
        fi

        if [[ "$VIRTUAL_ENV" == "" ]]; then
            source "$destfull"venv/bin/activate
        fi

        DJANGO_SETTINGS_MODULE="probemanager.settings.$arg"
        export DJANGO_SETTINGS_MODULE
        export PYTHONPATH=$PYTHONPATH:"$destfull"/probemanager
    else
        if [ ! -d venv ]; then
            python3 -m venv venv
            source venv/bin/activate
            venv/bin/pip3 install wheel
            venv/bin/pip3 install -r requirements/dev.txt
            venv/bin/pip3 install -r requirements/test.txt
        fi

        if [[ "$VIRTUAL_ENV" == "" ]]; then
            source venv/bin/activate
        fi

        DJANGO_SETTINGS_MODULE="probemanager.settings.$arg"
        export DJANGO_SETTINGS_MODULE
        export PYTHONPATH=$PYTHONPATH:$PWD/probemanager
    fi
}

generate_keys(){
    echo '## Generate secret_key and fernet_key ##'
    "$destfull"venv/bin/python "$destfull"probemanager/scripts/secrets.py -d $destfull
}

set_host(){
    if [ $arg == 'prod' ]; then
        echo '## Set Host file ##'
        echo "Give the host, followed by [ENTER]:"
        read host
        echo "[DEFAULT]" > "$destfull"conf.ini
        echo "HOST = $host" >> "$destfull"conf.ini
    fi
}

set_timezone(){
    echo '## Set Timezone ##'
    echo "Give the timezone, followed by [ENTER], example: Europe/Paris, default: UTC:"
    read timezone
    if [ "$timezone" == "" ]; then
        $timezone='UTC'
    fi
    if [ $arg == 'prod' ]; then
        echo "TIME_ZONE = $timezone" >> "$destfull"conf.ini
    fi
}

set_smtp(){
    if [ $arg == 'prod' ]; then
        echo '## Set SMTP settings ##'
        "$destfull"venv/bin/python "$destfull"probemanager/manage.py runscript setup_smtp --settings=probemanager.settings.$arg --script-args $destfull
    fi
}

set_log() {
    echo '## Set logs ##'
    if [ $arg == 'prod' ]; then
        echo "[LOG]" >> "$destfull"conf.ini
        echo "FILE_PATH = /var/log/probemanager.log" >> "$destfull"conf.ini
        echo "FILE_ERROR_PATH = /var/log/probemanager-error.log" >> "$destfull"conf.ini
    fi
}

set_settings() {
    echo '## Set settings ##'
    if [ $arg == 'prod' ]; then
        export DJANGO_SETTINGS_MODULE="probemanager.settings.$arg"
        # if there is not django settings in activate script
        if ! cat "$destfull"venv/bin/activate | grep -qw DJANGO_SETTINGS_MODULE ; then
            echo DJANGO_SETTINGS_MODULE="probemanager.settings.$arg" >> "$destfull"venv/bin/activate
            echo "export DJANGO_SETTINGS_MODULE" >> "$destfull"venv/bin/activate
            echo "export PYTHONPATH=""$destfull""probemanager" >> "$destfull"venv/bin/activate
            echo "export PATH=$PATH:""$destfull""venv/bin" >> "$destfull"venv/bin/activate
        fi
    else
        export DJANGO_SETTINGS_MODULE="probemanager.settings.$arg"
        # if there is not django settings in activate script
        if ! cat venv/bin/activate | grep -qw DJANGO_SETTINGS_MODULE ; then
            echo DJANGO_SETTINGS_MODULE="probemanager.settings.$arg" >> venv/bin/activate
            echo "export DJANGO_SETTINGS_MODULE" >> venv/bin/activate
            echo "export PYTHONPATH=$PYTHONPATH:$PWD/probemanager" >> venv/bin/activate
        fi
    fi
}

generate_version(){
    echo '## Generate version ##'
    if [ $arg == 'prod' ]; then
        "$destfull"venv/bin/python "$destfull"probemanager/manage.py runscript version --settings=probemanager.settings.$arg --script-args $destfull $(pwd)
    else
        venv/bin/python probemanager/manage.py runscript version --settings=probemanager.settings.$arg --script-args -
    fi
}

create_db() {
    echo '## Create DB ##'
    if [ -f /etc/debian_version ]; then
        sudo service postgresql restart
        sleep 5
        sudo su postgres -c 'dropdb --if-exists probemanager'
        sudo su postgres -c 'dropuser --if-exists probemanager'
        if [ $arg == 'prod' ]; then
            password=$("$destfull"venv/bin/python probemanager/scripts/db_password.py -d $destfull 2>&1)
            sudo su postgres -c "psql -c \"CREATE USER probemanager WITH LOGIN CREATEDB ENCRYPTED PASSWORD '$password';\""
        else
            sudo su postgres -c "psql -c \"CREATE USER probemanager WITH LOGIN CREATEDB ENCRYPTED PASSWORD 'probemanager';\""
        fi
        sudo su postgres -c 'createdb -T template0 -O probemanager probemanager'
    fi
    if [[ $OSTYPE == *"darwin"* ]]; then
        brew services restart postgresql
        sleep 5
        dropdb --if-exists probemanager
        dropuser --if-exists probemanager
        if [ $arg == 'prod' ]; then
            password=$("$destfull"venv/bin/python probemanager/scripts/db_password.py -d $destfull 2>&1)
            psql -d postgres -c "CREATE USER probemanager WITH LOGIN CREATEDB ENCRYPTED PASSWORD '$password';"
        else
            psql -d postgres -c "CREATE USER probemanager WITH LOGIN CREATEDB ENCRYPTED PASSWORD 'probemanager';"
        fi
        createdb -T template0 -O probemanager probemanager
    fi

    if [ $arg == 'prod' ]; then
        "$destfull"venv/bin/python "$destfull"probemanager/manage.py makemigrations --settings=probemanager.settings.$arg
        "$destfull"venv/bin/python "$destfull"probemanager/manage.py migrate --settings=probemanager.settings.$arg
        "$destfull"venv/bin/python "$destfull"probemanager/manage.py loaddata init.json --settings=probemanager.settings.$arg
        "$destfull"venv/bin/python "$destfull"probemanager/manage.py loaddata crontab.json --settings=probemanager.settings.$arg
    else
        venv/bin/python probemanager/manage.py makemigrations --settings=probemanager.settings.$arg
        venv/bin/python probemanager/manage.py migrate --settings=probemanager.settings.$arg
        venv/bin/python probemanager/manage.py loaddata init.json --settings=probemanager.settings.$arg
        venv/bin/python probemanager/manage.py loaddata crontab.json --settings=probemanager.settings.$arg
    fi
    for f in probemanager/*; do
        if [[ -d $f ]]; then
            if test -f "$f"/init_db.sh ; then
                ./"$f"/init_db.sh $arg $destfull
            fi
        fi
    done
}

update_db(){
    echo '## Update DB ##'
    "$destfull"venv/bin/python "$destfull"probemanager/manage.py makemigrations --settings=probemanager.settings.$arg
    "$destfull"venv/bin/python "$destfull"probemanager/manage.py migrate --settings=probemanager.settings.$arg
}

create_superuser(){
    echo '## Create Super user ##'
    if [ $arg == 'prod' ]; then
        "$destfull"venv/bin/python "$destfull"probemanager/manage.py createsuperuser --settings=probemanager.settings.$arg
    else
        venv/bin/python probemanager/manage.py createsuperuser --settings=probemanager.settings.$arg
    fi
}

collect_static(){
    echo '## Collect static ##'
    "$destfull"venv/bin/python "$destfull"probemanager/manage.py collectstatic --noinput --settings=probemanager.settings.$arg
}

check_deployement(){
    echo '## Check deployment ##'
    result=$( "$destfull"venv/bin/python "$destfull"probemanager/manage.py check --deploy --settings=probemanager.settings.$arg )
    result=$( "$destfull"venv/bin/python "$destfull"probemanager/manage.py validate_templates --settings=probemanager.settings.$arg )
}

generate_doc(){
    echo '## Generate doc ##'
    if [ $arg == 'prod' ]; then
        export DJANGO_SETTINGS_MODULE=probemanager.settings.$arg
        "$destfull"venv/bin/python "$destfull"probemanager/manage.py runscript generate_doc --settings=probemanager.settings.$arg
        "$destfull"venv/bin/sphinx-build -b html "$destfull"docs "$destfull"docs/_build/html
    else
        export DJANGO_SETTINGS_MODULE=probemanager.settings.$arg
        venv/bin/python probemanager/manage.py runscript generate_doc --settings=probemanager.settings.$arg
        venv/bin/sphinx-build -b html docs docs/_build/html
    fi
}

setup_tests(){
    echo '## Setup tests ##'
    venv/bin/python probemanager/manage.py runscript setup_tests --settings=probemanager.settings.$arg
}

apache_conf(){
    echo '## Create Apache configuration ##'
    "$destfull"venv/bin/python "$destfull"probemanager/manage.py runscript apache --script-args $destfull
}

update_repo(){
    echo '## Update Git repository ##'
    branch=$( git branch | grep \* | cut -d ' ' -f2 )
    git pull origin $branch
    git submodule update --remote
}

launch_celery(){
    if [ ! -f "$destfull"probemanager/celery.pid ]; then
        echo '## Start Celery ##'
        (cd "$destfull"probemanager/ && "$destfull"venv/bin/celery -A probemanager worker -D --pidfile celery.pid -B -l info -f /var/log/probemanager-celery.log --scheduler django_celery_beat.schedulers:DatabaseScheduler)
    else
        echo '## Restart Celery ##'
        kill $( cat "$destfull"probemanager/celery.pid)
        pkill -f celery
        sleep 5
        (cd "$destfull"probemanager/ && "$destfull"venv/bin/celery -A probemanager worker -D --pidfile celery.pid -B -l info -f /var/log/probemanager-celery.log --scheduler django_celery_beat.schedulers:DatabaseScheduler)
    fi
}

post_install() {
    echo '## Post Install ##'
    chown -R www-data:www-data "$destfull"
    # chmod -R 400 "$destfull"
    if [ -f /etc/apache2/sites-enabled/probemanager.conf ]; then
         chown www-data:www-data /etc/apache2/sites-enabled/probemanager.conf
    fi
    chmod 400 "$destfull"fernet_key.txt
    chmod 400 "$destfull"secret_key.txt
    chmod 400 "$destfull"password_db.txt
    chmod 400 "$destfull"conf.ini

    if [ ! -d /var/www/.ansible ]; then
        mkdir /var/www/.ansible
        chown www-data:www-data /var/www/.ansible
    fi
    touch /var/log/probemanager.log
    touch /var/log/probemanager-error.log
    chown www-data /var/log/probemanager.log
    chown www-data /var/log/probemanager-error.log
    a2dissite 000-default.conf
    a2dismod deflate -f
    systemctl restart apache2
}

# Install or update ?
if [ $arg == 'prod' ]; then
    if [ ! -d $dest'/ProbeManager' ]; then
        echo 'First prod install'
        echo 'Install in dir : '$destfull
        mkdir $dest/ProbeManager

        update_repo
        clean
        copy_files
        installOsDependencies
        installVirtualEnv
        set_host
        set_timezone
        set_log
        setGit
        set_smtp
        chooseApps
        set_settings
        install_modules
        generate_keys
        create_db
        generate_version
        create_superuser
        collect_static
        check_deployement
        generate_doc
        apache_conf
        post_install
        launch_celery

    else
        echo 'Update prod install'

        update_repo
        clean
        copy_files
        generate_version
        update_db
        collect_static
        check_deployement
        generate_doc
        post_install
        launch_celery
    fi
else
    echo 'Install for Development'

    clean
    installOsDependencies
    installVirtualEnv
    set_settings
    setGit
    set_smtp
    install_modules
    generate_version
    create_db
    create_superuser
    generate_doc
    setup_tests
fi

exit
