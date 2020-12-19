#! /bin/bash

. /home/stuser/venv_py37_st/bin/activate

gunicorn --workers 3 \
       	application:app \
	      -k meinheld.gmeinheld.MeinheldWorker \
	      --bind unix:stweb.sock \
        -m 007
