#!/bin/sh
REPO_ROOT="$(dirname $( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P ))"
COLLECTION_INSTALL=${COLLECTION_INSTALL:-true}
PIP_INSTALL=${PIP_INSTALL:-true}

if [ "$PIP_INSTALL" = true ]; then
    pip install -r $REPO_ROOT/requirements.txt
fi
if [ "$COLLECTION_INSTALL" = true ]; then
    ansible-galaxy install -r $REPO_ROOT/requirements.yml
fi