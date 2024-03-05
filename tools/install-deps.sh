#!/bin/sh
REPO_ROOT="$(dirname $( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P ))"

pip install -r $REPO_ROOT/requirements.txt
ansible-galaxy install -r $REPO_ROOT/requirements.yml