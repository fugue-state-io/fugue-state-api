#!/bin/bash
export FUGUE_STATE_CDN_ACCESS_ID="$(kubectl get secret -n api api-secrets -o json | jq -r '.data | map_values(@base64d) | ."FUGUE_STATE_CDN_ACCESS_ID"')"
export FUGUE_STATE_CDN_SECRET_KEY="$(kubectl get secret -n api api-secrets -o json | jq -r '.data | map_values(@base64d) | ."FUGUE_STATE_CDN_SECRET_KEY"')"