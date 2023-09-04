FROM python:3.11-slim

COPY poetry.lock pyproject.toml app/

RUN apt -y update \
    && pip install --upgrade pip \
    && pip install --no-cache-dir \
    && poetry install

WORKDIR /app

COPY ./src .

EXPOSE 8080

CMD python3 src/main.py
