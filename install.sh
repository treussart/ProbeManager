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

installDependencies() {
    echo '## Install Dependencies ##'
    # Debian
    if [ -f /etc/debian_version ]; then
        if ! type rabbitmq-server ; then
            apt install rabbitmq-server
        fi
        if ! apt list postgresql | grep -qw [installed] ; then
            apt install postgresql
        fi
        if ! apt list python3-virtualenv | grep -qw [installed] ; then
            apt install python3-venv
        fi
        if !  apt list gcc | grep -qw [installed] ; then
             apt install gcc
        fi
        if !  apt list python3-dev | grep -qw [installed] ; then
             apt install python3-dev
        fi
        if !  apt list make | grep -qw [installed] ; then
             apt install make
        fi
        if [ $arg == 'prod' ]; then
            if !  apt list apache2 | grep -qw [installed] ; then
                 apt install apache2
            fi
            if !  apt list libapache2-mod-wsgi-py3 | grep -qw [installed] ; then
                 apt install libapache2-mod-wsgi-py3
            fi
        fi
    fi
    # OSX with brew
    if [[ $OSTYPE == *"darwin"* ]]; then
        if brew --version | grep -qw Homebrew ; then
            if ! brew list | grep -qw rabbitmq ; then
                brew install rabbitmq
            fi
            if ! brew list | grep -qw postgresql ; then
                brew install postgresql
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
            "$destfull"venv/bin/pip3 install -r requirements.txt
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
            venv/bin/pip3 install -r requirements.txt
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

set_smtp(){
    if [ $arg == 'prod' ]; then
        echo '## Set SMTP settings ##'
        "$destfull"venv/bin/python "$destfull"probemanager/manage.py runscript setup_smtp --settings=probemanager.settings.$arg --script-args $destfull
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
        service postgresql restart
        sleep 5
        su postgres -c 'dropdb --if-exists probemanager'
        su postgres -c 'dropuser probemanager'
        if [ $arg == 'prod' ]; then
            password=$("$destfull"venv/bin/python probemanager/scripts/db_password.py -d $destfull 2>&1)
            su postgres -c "psql -c \"CREATE USER probemanager WITH LOGIN CREATEDB ENCRYPTED PASSWORD '$password';\""
        else
            su postgres -c "psql -c \"CREATE USER probemanager WITH LOGIN CREATEDB ENCRYPTED PASSWORD 'probemanager';\""
        fi
        su postgres -c 'createdb -T template0 -O probemanager probemanager'
    fi
    if [[ $OSTYPE == *"darwin"* ]]; then
        brew services restart postgresql
        sleep 5
        dropdb --if-exists probemanager
        dropuser probemanager
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
    "$destfull"venv/bin/python "$destfull"probemanager/manage.py loaddata init.json --settings=probemanager.settings.$arg
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
        "$destfull"venv/bin/python "$destfull"probemanager/manage.py runscript generate_doc --settings=probemanager.settings.$arg --script-args $destfull
    else
        venv/bin/python probemanager/manage.py runscript generate_doc --settings=probemanager.settings.$arg --script-args -
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

update_depot(){
    echo '## Update Git repository ##'
    git pull origin master
    git submodule update --remote
}

launch_celery(){
    if [ ! -f "$destfull"probemanager/celery.pid ]; then
        echo '## Start Celery ##'
        (cd "$destfull"probemanager/ && "$destfull"venv/bin/celery -A probemanager worker -D --pidfile celery.pid -B -l info -f celery.log --scheduler django_celery_beat.schedulers:DatabaseScheduler)
    else
        echo '## Restart Celery ##'
        kill $( cat "$destfull"probemanager/celery.pid)
        pkill -f celery
        sleep 5
        (cd "$destfull"probemanager/ && "$destfull"venv/bin/celery -A probemanager worker -D --pidfile celery.pid -B -l info -f celery.log --scheduler django_celery_beat.schedulers:DatabaseScheduler)
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

        clean

        copy_files
        installDependencies
        installVirtualEnv
        set_host
        chooseApps
        install_modules
        set_settings
        setGit
        generate_keys
        create_db
        generate_version
        set_smtp
        create_superuser
        collect_static
        check_deployement
        generate_doc
        apache_conf
        post_install
        launch_celery

    else
        echo 'Update prod install'

        update_depot
        clean
        copy_files
        set_settings
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
    installDependencies
    installVirtualEnv
    install_modules
    set_settings
    setGit
    generate_version
    create_db
    create_superuser
    generate_doc
    setup_tests
fi

exit
