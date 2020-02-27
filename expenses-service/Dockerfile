FROM python:3.8

RUN pip3 install --upgrade pip

RUN mkdir /usr/src/expenses-service
WORKDIR /usr/src/expenses-service


COPY ./req.pip .
RUN pip3 install --no-cache-dir -r req.pip

COPY ./wsgi.py .
RUN mkdir ./service_app
COPY ./service_app/ ./service_app/

EXPOSE 8000
