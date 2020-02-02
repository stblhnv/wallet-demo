FROM python:3.7-alpine3.11

LABEL version="1.0"
LABEL maintainer="stblhnv@gmail.com"

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY . /srv/api-backend/

WORKDIR /srv/api-backend/

RUN apk update && \
    apk add gcc \
        musl-dev \
        libffi-dev \
        libressl-dev \
        make \
        zlib-dev \
        jpeg-dev \
        postgresql-dev \
        postgresql-client && \
    pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-dev --no-interaction --no-ansi

EXPOSE 8000
