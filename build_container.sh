#!/bin/bash
set -e
export BOOTSTRAP_PATH=$(realpath "$0")
export WORKING_DIRECTORY=$(dirname $BOOTSTRAP_PATH)

docker build . -f ./Dockerfile -t registry.digitalocean.com/fugue-state-registry/fugue-state-api:local