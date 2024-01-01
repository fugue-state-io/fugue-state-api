#!/bin/bash
set -e 
docker build . -f ./Dockerfile -t registry.digitalocean.com/fugue-state-registry/fugue-state-api:local