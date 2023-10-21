FROM python:3.11

COPY . /srv/flask_app
WORKDIR /srv/flask_app
RUN pip install -r requirements.txt --src /usr/local/src
RUN apt update
RUN apt install ffmpeg nginx build-essential python3-dev uwsgi -y
RUN pytest

COPY nginx.conf /etc/nginx
RUN chmod +x ./start.sh
CMD ["./start.sh"]
