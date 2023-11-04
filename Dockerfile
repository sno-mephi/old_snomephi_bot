# syntax=docker/dockerfile:1
FROM python:3.9-slim-buster
WORKDIR /app
RUN pip3 install aiogram
COPY modules modules/
COPY initializer.py initializer.py
COPY main.py main.py
COPY jsondriver.py jsondriver.py
CMD [ "python3", "main.py"]
