
# fugue-state-api
The fugue-state-api can be run locally with the following command.
`flask --app api/src run`

## Tests
To run tests execute the following command
`pytest`

## Dockerfile and uwsgi
The production build of this application uses docker and nginx with uwsgi.
https://smirnov-am.github.io/running-flask-in-production-with-docker/
### CI/CD Pipeline
argo-workflows.fugue-state.io holds the Continuous Integration workflows.
argocd.fugue-state.io holds the Continuous Delivery pipelines.
---
In order to modify the continuous integration workflows edit this helm chart https://github.com/fugue-state-io/helm-charts/tree/develop/ci/templates
In order to modify the continuous delivery workflow edit this helm chart https://github.com/fugue-state-io/helm-charts/tree/develop/fugue-state-api/templates
### Manual Release.
run
`publish.sh`
## end-points
The api serves the following endpoints

### `/api/process_audo`
Takes an `.mp3` file and returns the waveform as a `.png`   