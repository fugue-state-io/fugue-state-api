#!/bin/bash
set -e
docker run -p 5000:5000 registry.digitalocean.com/fugue-state-registry/fugue-state-api:local