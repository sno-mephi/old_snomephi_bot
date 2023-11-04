# syntax=docker/dockerfile:1
FROM python:3.9-slim-buster
WORKDIR /app
RUN pip3 install aiogram==2.25.2
COPY modules modules/
COPY initializer.py initializer.py
COPY main.py main.py
COPY config.py config.py
COPY jsondriver.py jsondriver.py

COPY db_prod db_prod/
COPY db_test db_test/
CMD [ "python3", "main.py"]
