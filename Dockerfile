FROM python:3.11-slim

ENV PYTHONUNBUFFERED 1
ENV POETRY_HOME /opt/poetry
ENV PATH $POETRY_HOME/bin:$PATH
ENV POETRY_VIRTUALENVS_CREATE=false
ENV POETRY_VERSION=1.6.1

COPY poetry.lock pyproject.toml app/
WORKDIR /app

RUN apt -y update \
    && pip install --upgrade pip \
    && pip install --no-cache-dir "poetry==$POETRY_VERSION" \
    && poetry install --no-root

COPY ./src .

EXPOSE 8080
