FROM python:3.11
COPY ./api/ ./
COPY ./requirements.txt ./requirements.txt
RUN pip install -r requirements.txt
RUN apt update
RUN apt install ffmpeg -y
CMD flask --app main run