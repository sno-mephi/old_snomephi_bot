FROM python:3.9-slim-buster
WORKDIR /app
RUN pip3 install aiogram==2.25.2

COPY modules modules/
COPY initializer.py initializer.py
COPY main.py main.py
COPY config.py config.py
COPY jsondriver.py jsondriver.py
COPY salert_utils.py salert_utils.py

COPY db_prod db_prod/
COPY db_test db_test/

ENV TZ=Europe/Moscow
ENV TESTING_MODE=true

# Если переменная окружения TESTING_MODE установлена в true, выполнится CMD [ "python3", "main.py", "--testing"]
CMD [ "sh", "-c", "if [ \"$TESTING_MODE\" = \"true\" ]; then python3 main.py --testing; else python3 main.py; fi" ]

# Для запуска в тестинге использовать docker run -e TESTING_MODE=true
# для запуска в проде docker run -e TESTING_MODE=true -v $(pwd)/db_prod:/app/db_prod имя_образа

# RECOMMENDED COMMANDS:
# (suppose you run it in app root dir)
# BUILD: docker build old_snomephi_bot .
# RUN:   docker run -e TESTING_MODE=true -v $(pwd)/db_prod:/app/db_prod --name old_snomephi_bot --rm old_snomephi_bot
# STOP:  docker stop old_snomephi_bot