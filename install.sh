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
if [ -z $1 ] || [[ "$1" = 'dev' ]]; then
    arg="dev"
    dest=$( pwd )
elif [[ "$1" = 'prod' ]]; then
    arg=$1
    if [ -z $2 ]; then
        dest='/usr/local/share'
    elif [[ "$2" = "." ]]; then
        dest=$( pwd )
    else
        dest=$2
    fi
elif [[ "$1" = 'help' ]]; then
    echo "$HELP"
    exit
else
    echo 'Bad argument'
    exit 1
fi
if [[ "$dest" = $( pwd ) ]]; then
    destfull="$dest"/
else
    destfull="$dest"/ProbeManager/
fi

install_modules(){
    echo '## Install the modules ##'
    for f in probemanager/*; do
        if [[ -d $f ]]; then
            if test -f "$f"/install.sh ; then
                ./"$f"/install.sh "$arg" "$destfull"
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
    if [[ "$arg" = 'prod' ]]; then
        echo '## Copy files in install dir ##'
        if [[ "$destfull" != $( pwd )/ ]]; then # Don't copy in the same directory
            if [ -d $destfull ]; then
                # copy the project
                cp -r probemanager $destfull
                # copy the doc
                cp -r docs $destfull
                # copy the start script for test
                cp start.sh $destfull
                cp README.rst $destfull
            fi
        fi
    fi
}

install_os_dependencies() {
    echo '## Install Dependencies ##'
    # Debian
    if [ -f /etc/debian_version ]; then
        sudo apt update
        grep -v "#" requirements/os/debian.txt | grep -v "^$" | xargs sudo apt install -y
        if [[ "$arg" = 'prod' ]]; then
            grep -v "#" requirements/os/debian_prod.txt | grep -v "^$" | xargs sudo apt install -y
        fi
    fi
    # OSX with brew
    if [[ $OSTYPE == *"darwin"* ]]; then
        if brew --version | grep -qw Homebrew ; then
            grep -v "#" requirements/os/osx.txt | grep -v "^$" | xargs brew install
            if [[ "$arg" = 'prod' ]]; then
                grep -v "#" requirements/os/osx_prod.txt | grep -v "^$" | xargs brew install
            fi
        fi
    fi
}

select_apps(){
    if [[ "$arg" = 'prod' ]]; then
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
                text=$text"'$i'"
            else
                text=$text", '$i'"
            fi
        done
        echo "Module(s) available : "${apps[*]}
        echo "[APPS]" >> "$destfull"conf.ini
        echo "PROD_APPS = [$text]" >> "$destfull"conf.ini
    fi
}

set_git(){
    echo '## Set Git ##'
    git_bin=$( which git )
    echo "[GIT]" >> "$destfull"conf.ini
    echo "GIT_BINARY = $git_bin" >> "$destfull"conf.ini
}

install_virtualenv() {
    if [[ "$VIRTUAL_ENV" = "" ]]; then
        if [ ! -d "$destfull"venv ]; then
            echo '## Create Virtualenv ##'
            python3 -m venv "$destfull"venv
        fi
        source "$destfull"venv/bin/activate
    fi
    echo '## Install Pip package ##'
    pip install wheel
    if [[ "$arg" = 'prod' ]] && [[ "$TRAVIS" != true ]]; then
        pip install -r requirements/prod.txt
    elif [[ "$TRAVIS" = true ]]; then
        pip install -r requirements/prod.txt
        pip install -r requirements/test.txt
    else
        pip install -r requirements/dev.txt
        pip install -r requirements/test.txt
    fi
    export DJANGO_SETTINGS_MODULE="probemanager.settings.$arg"
    export PYTHONPATH=$PYTHONPATH:"$destfull"/probemanager
}

generate_keys(){
    if [[ "$arg" = 'prod' ]]; then
        echo '## Generate secret_key and fernet_key ##'
        python "$destfull"probemanager/scripts/secrets.py -d $destfull
    fi
}

set_host(){
    if [[ "$arg" = 'prod' ]]; then
        echo '## Set Host file ##'
        if [[ "$TRAVIS" = true ]]; then
            host='probemanager.test.com'
        else
            echo "Give the host, followed by [ENTER]:"
            read host
        fi
        echo "[DEFAULT]" > "$destfull"conf.ini
        echo "HOST = $host" >> "$destfull"conf.ini
    fi
}

set_timezone(){
    if [[ "$arg" = 'prod' ]]; then
        echo '## Set Timezone ##'
        if [[ "$TRAVIS" = true ]]; then
            timezone='Europe/Paris'
        else
            echo "Give the timezone, followed by [ENTER], example: Europe/Paris, default: UTC:"
            read timezone
        fi
        if [ "$timezone" == "" ]; then
            $timezone='UTC'
        fi
        if [[ "$arg" = 'prod' ]]; then
            echo "TIME_ZONE = $timezone" >> "$destfull"conf.ini
        fi
    fi
}

set_smtp(){
    if [[ "$arg" = 'prod' ]] && [[ "$TRAVIS" != true ]]; then
        echo '## Set SMTP settings ##'
        python "$destfull"probemanager/scripts/setup_smtp.py -d $destfull
    fi
}

set_logs(){
    if [[ "$arg" = 'prod' ]]; then
        echo '## Set logs ##'
        echo "[LOG]" >> "$destfull"conf.ini
        echo "FILE_PATH = /var/log/probemanager.log" >> "$destfull"conf.ini
        echo "FILE_ERROR_PATH = /var/log/probemanager-error.log" >> "$destfull"conf.ini
        sudo touch /var/log/probemanager.log
        sudo touch /var/log/probemanager-error.log
        sudo chown $(whoami) /var/log/probemanager.log
        sudo chown $(whoami) /var/log/probemanager-error.log
    fi
}

generate_version(){
    echo '## Generate version ##'
    python "$destfull"probemanager/manage.py runscript version --settings=probemanager.settings.$arg --script-args $(pwd) $destfull
}

create_db() {
    echo '## Create DB ##'
    if [ -f /etc/debian_version ]; then
        sudo service postgresql restart
        sleep 5
        sudo su postgres -c 'dropdb --if-exists probemanager'
        sudo su postgres -c 'dropuser --if-exists probemanager'
        if [[ "$arg" = 'prod' ]] && [[ "$TRAVIS" != true ]]; then
            password=$(python probemanager/scripts/db_password.py -d $destfull 2>&1)
            sudo su postgres -c "psql -c \"CREATE USER probemanager WITH LOGIN CREATEDB ENCRYPTED PASSWORD '$password';\""
        else
            sudo su postgres -c "psql -c \"CREATE USER probemanager WITH LOGIN CREATEDB ENCRYPTED PASSWORD 'probemanager';\""
        fi
        sudo su postgres -c 'createdb -T template0 -O probemanager probemanager'
    elif [[ $OSTYPE == *"darwin"* ]]; then
        brew services restart postgresql
        sleep 5
        dropdb --if-exists probemanager
        dropuser --if-exists probemanager
        if [[ "$arg" = 'prod' ]]; then
            password=$(python probemanager/scripts/db_password.py -d $destfull 2>&1)
            psql -d postgres -c "CREATE USER probemanager WITH LOGIN CREATEDB ENCRYPTED PASSWORD '$password';"
        else
            psql -d postgres -c "CREATE USER probemanager WITH LOGIN CREATEDB ENCRYPTED PASSWORD 'probemanager';"
        fi
        createdb -T template0 -O probemanager probemanager
    fi
    python "$destfull"probemanager/manage.py makemigrations --settings=probemanager.settings.$arg
    python "$destfull"probemanager/manage.py migrate --settings=probemanager.settings.$arg
    python "$destfull"probemanager/manage.py loaddata init.json --settings=probemanager.settings.$arg
    python "$destfull"probemanager/manage.py loaddata crontab.json --settings=probemanager.settings.$arg
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
    python "$destfull"probemanager/manage.py makemigrations --settings=probemanager.settings.$arg
    python "$destfull"probemanager/manage.py migrate --settings=probemanager.settings.$arg
}

create_superuser(){
    if [[ "$TRAVIS" != true ]]; then
        echo '## Create Super user ##'
        python "$destfull"probemanager/manage.py createsuperuser --settings=probemanager.settings.$arg
    fi
}

collect_static(){
    if [[ "$arg" = 'prod' ]]; then
        echo '## Collect static ##'
        python "$destfull"probemanager/manage.py collectstatic --noinput --settings=probemanager.settings.$arg
    fi
}

check_deployement(){
    if [[ "$arg" = 'prod' ]]; then
        echo '## Check deployment ##'
        python "$destfull"probemanager/manage.py check --deploy --settings=probemanager.settings.$arg
        python "$destfull"probemanager/manage.py validate_templates --settings=probemanager.settings.$arg
    fi
}

generate_doc(){
    echo '## Generate doc ##'
    python "$destfull"probemanager/manage.py runscript generate_doc --settings=probemanager.settings.$arg
    sphinx-build -b html "$destfull"docs "$destfull"docs/_build/html
}

setup_tests(){
    if [[ "$arg" = 'dev' ]]; then
        echo '## Setup tests ##'
        python "$destfull"probemanager/manage.py runscript setup_tests --settings=probemanager.settings.$arg
    fi
}

apache_conf(){
    if [[ "$arg" = 'prod' ]]; then
        echo '## Create Apache configuration ##'
        sudo touch /etc/apache2/sites-enabled/probemanager.conf
        sudo chown $(whoami) /etc/apache2/sites-enabled/probemanager.conf
        python "$destfull"probemanager/manage.py runscript apache --script-args $destfull
    fi
}

update_repo(){
    if [[ "$TRAVIS" != true ]]; then
        echo '## Update Git repository ##'
        branch=$( git branch | grep \* | cut -d ' ' -f2 )
        git pull origin $branch
        git submodule update --remote
    fi
}

launch_celery(){
    if [[ "$arg" = 'prod' ]]; then
        sudo touch /var/log/probemanager-celery.log
        sudo chown $(whoami) /var/log/probemanager-celery.log
        if [ ! -f "$destfull"probemanager/celery.pid ]; then
            echo '## Start Celery ##'
            (cd "$destfull"probemanager/ && sudo celery -A probemanager worker -D --pidfile celery.pid -B -l info -f /var/log/probemanager-celery.log --scheduler django_celery_beat.schedulers:DatabaseScheduler)
        else
            echo '## Restart Celery ##'
            sudo kill $( cat "$destfull"probemanager/celery.pid)
            sudo pkill -f celery
            if [ -f "$destfull"probemanager/celery.pid ]; then
                sudo rm "$destfull"probemanager/celery.pid
            fi
            sleep 8
            (cd "$destfull"probemanager/ && sudo celery -A probemanager worker -D --pidfile celery.pid -B -l info -f /var/log/probemanager-celery.log --scheduler django_celery_beat.schedulers:DatabaseScheduler)
        fi
    fi
}

post_install() {
    if [[ "$arg" = 'prod' ]]; then
        echo '## Post Install ##'
        sudo chown -R www-data:$(whoami) "$destfull"
        if [ -f /etc/apache2/sites-enabled/probemanager.conf ]; then
             sudo chown www-data:www-data /etc/apache2/sites-enabled/probemanager.conf
        fi
        sudo chmod 440 "$destfull"fernet_key.txt
        sudo chmod 440 "$destfull"secret_key.txt
        if [ -f "$destfull"password_db.txt ]; then
            sudo chmod 440 "$destfull"password_db.txt
        fi
        sudo chmod 440 "$destfull"conf.ini

        sudo chown www-data:$(whoami) /var/log/probemanager.log
        sudo chown www-data:$(whoami) /var/log/probemanager-error.log
        sudo a2dissite 000-default.conf
        sudo a2dismod deflate -f
        sudo service apache2 restart
    fi
}

first=false
if [ ! -d "$destfull" ]; then
    sudo mkdir $destfull
    sudo chown $(whoami) $destfull
    first=true
elif [ ! -f "$destfull"probemanager/version.txt ]; then
    first=true
fi

export DJANGO_SETTINGS_MODULE="probemanager.settings.$arg"
export PYTHONPATH=$PYTHONPATH:"$destfull"/probemanager

if [ "$first" = true ]; then
    echo 'First install'
    echo 'Install in dir : '$destfull

    update_repo
    clean
    copy_files
    install_os_dependencies
    install_virtualenv
    set_host
    set_timezone
    set_logs
    set_git
    generate_keys
    select_apps
    set_smtp
    install_modules
    create_db
    generate_version
    create_superuser
    collect_static
    check_deployement
    generate_doc
    setup_tests
    apache_conf
    launch_celery
    post_install

else
    echo 'Update install'

    update_repo
    copy_files
    install_virtualenv
    generate_version
    update_db
    collect_static
    check_deployement
    generate_doc
    launch_celery
    post_install
fi

exit
