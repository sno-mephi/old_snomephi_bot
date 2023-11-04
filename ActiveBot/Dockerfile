# syntax=docker/dockerfile:1
FROM python:3.9-slim-buster
WORKDIR /app
RUN pip3 install aiogram wikipedia requests
COPY main.py main.py
CMD [ "python3", "main.py"]
