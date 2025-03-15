#!/bin/bash
set -x

TAGNAME=kstack-agent
REGISTRY=fmlabs

VERSION=0.0.0
if [[ -f VERSION ]]; then
  VERSION=$(cat VERSION)
fi

RELEASE=
if [[ $1 == "--release" ]]; then
  RELEASE=1
  shift
fi

if ! docker build -t ${TAGNAME}:latest --progress=plain -f ./Dockerfile-alpine .
then
  echo "DOCKER BUILD FAILED"
  exit 1
fi



if [[ $RELEASE == "1" ]]; then
  echo "Creating release ..."

  if ! docker build -t ${TAGNAME}:${VERSION} .
  then
    echo "DOCKER BUILD FAILED"
    exit 1
  fi

  if ! docker tag ${TAGNAME}:${VERSION} ${REGISTRY}/${TAGNAME}:${VERSION} ; then
    echo "DOCKER REGISTRY VERSION TAGGING FAILED"
    exit 1
  fi

  if ! docker push ${REGISTRY}/${TAGNAME}:${VERSION} ; then
    echo "DOCKER PUSH FAILED"
    exit 1
  fi

fi


docker scout cves ${TAGNAME}:latest