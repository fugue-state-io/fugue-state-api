#!/bin/bash
set -e
#python -m gunicorn api.src:app
flask --app api/src run