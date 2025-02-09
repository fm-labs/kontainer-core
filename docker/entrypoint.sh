#!/bin/bash

KUSER=kstack

init_services() {

  if ! service nginx start ; then
    echo "Failed to start nginx"
    tail /var/log/nginx/error.log
    exit 1
  fi
}

trap_handler() {
  echo "Trap received signal. Exiting ..."
  exit
}
trap trap_handler SIGINT SIGTERM SIGABRT SIGQUIT SIGUSR1 SIGUSR2


CURRENTUSER=`whoami`
CURRENTUSERID=`id`

echo "WHOAMI: ${CURRENTUSER} / ${KUSER}"
echo "ID: ${CURRENTUSERID} / ${KUSER_ID}"

export PYTHON_UNBUFFERED=1
export PYTHONPATH=/app/src:$PYTHONPATH
export AGENT_DATA_DIR=/app/data
export AGENT_HOST=0.0.0.0
export AGENT_PORT=5000

# Gunicorn settings
NAME="kstack-agent-api"
USER=$(whoami)
GROUP=$(whoami)
NUM_WORKERS=3
WSGI_APP=wsgi:app
LOG_LEVEL=debug # todo change to info in production

case $1 in

  "devserver")
    init_services

    echo "Starting devserver ..."
    exec python3 /app/agent.py

    ;;

  "gunicorn-tcp")
    init_services

    BIND=0.0.0.0:5000
    echo "Starting gunicorn (${BIND}) ..."
    exec gunicorn ${WSGI_APP} \
      --name ${NAME} \
      --workers ${NUM_WORKERS} \
      --bind=${BIND} \
      --log-level=${LOG_LEVEL} \
      --log-file=-

    ;;

  "gunicorn-socket")
    init_services

    SOCKFILE=/run/gunicorn.sock
    BIND=unix:$SOCKFILE
    echo "Starting gunicorn (${BIND}) ..."
    exec gunicorn ${WSGI_APP} \
      --name ${NAME} \
      --workers ${NUM_WORKERS} \
      --bind=${BIND} \
      --log-level=${LOG_LEVEL} \
      --log-file=-

    ;;

  *)
    echo "Executing arbitrary command: $@"
    # exec su -c "$@" $KUSER
    exec "$@"

    ;;
esac
