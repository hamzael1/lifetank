FROM python:3.8

RUN mkdir /usr/src/tasks-service
WORKDIR /usr/src/tasks-service

RUN pip3 install --upgrade pip

COPY ./req.pip .
RUN pip3 install --no-cache-dir -r req.pip


RUN mkdir ./service_app
COPY ./service_app/ ./service_app/

EXPOSE 8000

