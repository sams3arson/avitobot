FROM python

ENV API_ID=
ENV API_HASH=
ENV BOT_TOKEN=
ENV OWNER_ID=

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY . .

RUN pip3 install -r requirements.txt

RUN cat avitobot.sql | sqlite3 avitobot.db

CMD ["python3", "main.py"]

