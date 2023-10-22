FROM python:3.11

COPY . /srv/flask_app
WORKDIR /srv/flask_app
RUN pip install -r requirements.txt --src /usr/local/src
RUN apt update
RUN apt install ffmpeg nginx build-essential python3-dev gunicorn -y
RUN pytest

# ENTRYPOINT [ "sh" ]
CMD gunicorn --conf=api/gunicorn_conf.py --bind 0.0.0.0:5000 api.src:app