#!/bin/bash
set -e
python -m gunicorn api.src:app