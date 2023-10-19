FROM python:3.11
COPY ./src/ ./
COPY ./requirements.txt ./requirements.txt
RUN pip install -r requirements.txt
CMD flask --app main run