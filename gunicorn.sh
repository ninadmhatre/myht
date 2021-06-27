#! /bin/bash

APP_ENV=${1:-"dev"}
echo "Running environment: [$APP_ENV]"

if [[ $APP_ENV == "prod" ]]; then
    . /home/stuser/venv_py37_st/bin/activate
    export APP_ENVIRONMENT="prod"
    BIND_TO=unix:stweb.sock
else
    export APP_ENVIRONMENT="dev"
    BIND_TO=localhost:8000
fi

# Set environment variables
export LOG_DIR=/var/log/stapp
export LOG_TYPE=watched
export LOG_LEVEL=info
export APP_LOG_NAME=app.log
export WWW_LOG_NAME=www.log

if [[ ! -d $LOG_DIR ]]; then
   echo "********************"
   echo "Error: LOG_DIR \'$LOG_DIR\' does not exist!" 
   echo "********************"
   exit 1
fi


gunicorn --workers 3 application:app -k meinheld.gmeinheld.MeinheldWorker --bind $BIND_TO -m 007
