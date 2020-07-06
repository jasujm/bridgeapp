FROM python:3.8 AS builder

RUN set -ex;                                 \
    mkdir -p /usr/src/bridgeapp;             \
    pip install poetry;                      \
    poetry config virtualenvs.create false;

WORKDIR /usr/src/bridgeapp

COPY . .

RUN poetry install --no-dev
