#!/bin/bash

#KUSER=kstack

init_services() {

  #mkdir -p /etc/nginx/ssl

  if [[ ! -f /etc/nginx/ssl/self-signed.crt ]]; then
    echo "Generating self-signed certificate ..."
    mkdir -p /etc/nginx/ssl
    openssl req -x509 -nodes -days 3650 -newkey rsa:2048 -keyout /etc/nginx/ssl/self-signed.key -out /etc/nginx/ssl/self-signed.crt -subj '/CN=localhost'
    RC=$?
    if [[ $RC != 0 ]]; then
      echo "ERROR: Failed to generate self-signed certificate"
      exit 1
    fi
  fi

  if [[ ! -f /etc/nginx/ssl/dhparam.pem ]]; then
    echo "Generating dhparam.pem ..."
    openssl dhparam -out /etc/nginx/ssl/dhparam.pem 2048
    RC=$?
    if [[ $RC != 0 ]]; then
      echo "ERROR: Failed to generate dhparam.pem"
      exit 1
    fi
  fi

  if [[ ! -f /etc/nginx/ssl/cert.pem ]]; then
    echo "Using self signed cert ..."
    ln -sf /etc/nginx/ssl/self-signed.crt /etc/nginx/ssl/cert.pem
    ln -sf /etc/nginx/ssl/self-signed.key /etc/nginx/ssl/key.pem
  fi

  if ! nginx -t ; then
    echo "ERROR: Failed to test nginx configuration"
    exit 1
  fi

  echo "Checking docker-compose ..."
  DOCKER_COMPOSE_BIN=`which docker-compose`
  DOCKER_COMPOSE_VERSION=`docker-compose --version`

  echo "DOCKER_COMPOSE_BIN: ${DOCKER_COMPOSE_BIN}"
  echo "DOCKER_COMPOSE_VERSION: ${DOCKER_COMPOSE_VERSION}"

  #  echo "Starting nginx ..."
  #  nginx -g "daemon off;" &
  #
  #  echo "Starting redis-server ..."
  #  redis-server &
  #
  #  if ! supervisord -c /etc/supervisord.conf ; then
  #    echo "ERROR: Failed to start supervisor"
  #    exit 1
  #  fi
  #
  #  supervisorctl reread && supervisorctl update
  #
  #  if ! supervisorctl start celery_worker ; then
  #    echo "WARN: Failed to start celery_worker"
  #    exit 1
  #  fi

  #if ! supervisorctl start app ; then
  #  echo "WARN: Failed to start app"
  #  #exit 1
  #fi

}

trap_handler() {
  echo "Trap received signal. Exiting ..."
  exit
}
trap trap_handler SIGINT SIGTERM SIGABRT SIGQUIT SIGUSR1 SIGUSR2


CURRENTUSER=`whoami`
CURRENTUSERID=`id`
echo "WHOAMI: ${CURRENTUSER}"
echo "ID: ${CURRENTUSERID}"


case $1 in

  "nginx")
  init_services
  exec nginx -g "daemon off;"
  ;;


  "supervisor")
  init_services
  exec /usr/bin/supervisord --nodaemon -c /etc/supervisord.conf
  ;;


  "devserver")
    init_services

    # Allow connections from any host
    # export AGENT_HOST=0.0.0.0

    echo "Starting devserver ..."
    export PYTHON_UNBUFFERED=1
    export PYTHONPATH=/app/src:$PYTHONPATH
    export DEBUG=true

    exec python3 /app/agent.py
    ;;


  "gunicorn-tcp")
    init_services

    # Only allow connections from localhost
    # export AGENT_HOST=127.0.0.1

    exec /app/bin/gunicorn_tcp.sh
    ;;

  "gunicorn-socket")
    init_services
    exec /app/bin/gunicorn_socket.sh
    ;;


  "celery-worker")
    exec /app/celery_worker.sh
    ;;


  *)
    echo "Executing arbitrary command: $@"
    # exec su -c "$@" $KUSER
    exec "$@"

    ;;
esac
