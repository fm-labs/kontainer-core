#!/bin/bash

KUSER=kstack

init_services() {

  if [[ ! -f /etc/ssl/self-signed.crt ]]; then
    echo "Generating self-signed certificate ..."
    mkdir -p /etc/ssl
    openssl req -x509 -nodes -days 3650 -newkey rsa:2048 -keyout /etc/ssl/self-signed.key -out /etc/ssl/self-signed.crt -subj '/CN=localhost'
  fi

  if [[ ! -f /etc/ssl/dhparam.pem ]]; then
    echo "Generating dhparam.pem ..."
    openssl dhparam -out /etc/ssl/dhparam.pem 2048
  fi

  if [[ ! -f /etc/ssl/cert.pem ]]; then
    echo "Using self signed cert ..."
    ln -sf /etc/ssl/self-signed.crt /etc/ssl/cert.pem
    ln -sf /etc/ssl/self-signed.key /etc/ssl/key.pem
  fi

  if ! service nginx start ; then
    echo "ERROR: Failed to start nginx"
    nginx -t
    tail /var/log/nginx/error.log
    exit 1
  fi

  if ! service redis-server start ; then
    echo "ERROR: Failed to start redis-server"
    tail /var/log/redis/redis-server.log
    #exit 1
  fi

  #if ! service supervisor restart ; then
  if ! supervisord -c /etc/supervisor/supervisord.conf ; then
    echo "ERROR: Failed to start supervisor"
    #tail /var/log/redis/redis-server.log
    exit 1
  fi

  if ! supervisorctl start celery_worker ; then
    echo "WARN: Failed to start celery_worker"
    #exit 1
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
export AGENT_DATA_DIR=${AGENT_DATA_DIR:-/app/data}
export AGENT_HOST=${AGENT_HOST:-0.0.0.0}
export AGENT_PORT=${AGENT_PORT:-5000}

# Gunicorn settings
NAME="kstack-agent-api"
USER=$(whoami)
GROUP=$(whoami)
WSGI_APP=wsgi:app
NUM_WORKERS=${AGENT_WORKERS:-3}
LOG_LEVEL=${LOG_LEVEL:-info}

case $1 in

  "devserver")
    init_services

    # Allow connections from any host
    # export AGENT_HOST=0.0.0.0

    echo "Starting devserver ..."
    exec python3 /app/agent.py
    ;;

  "gunicorn-tcp")
    init_services

    # Only allow connections from localhost
    # export AGENT_HOST=127.0.0.1

    # BIND=0.0.0.0:5000
    BIND=${AGENT_HOST}:${AGENT_PORT}
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

  "celery-worker")
    echo "Starting celery worker ..."
    exec /app/celery_worker.sh
    ;;

  *)
    echo "Executing arbitrary command: $@"
    # exec su -c "$@" $KUSER
    exec "$@"

    ;;
esac
