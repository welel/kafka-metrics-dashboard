FROM python:3.10-slim

WORKDIR /app

ENV DEBIAN_FRONTEND=noninteractive

COPY ./requirements.txt /app/requirements.txt

RUN pip --timeout=60000 install --upgrade pip \
    && pip --timeout=60000 install --no-cache-dir -r /app/requirements.txt

COPY . /app
