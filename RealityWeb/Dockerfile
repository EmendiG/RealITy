FROM python:3.8.5-slim

RUN apt-get update && \
    apt-get install -y \
    bash \
    build-essential \
    gcc \
    libffi-dev \
    musl-dev \
    openssl \
    postgresql \
    libpq-dev

ENV PYTHONUNBUFFERED=1
WORKDIR /app/

COPY requirements.txt ./requirements.txt
RUN pip install -r ./requirements.txt

COPY manage.py ./manage.py
COPY . .

COPY ./website_bootcommand.sh /website_bootcommand.sh
RUN chmod +x /website_bootcommand.sh
ENTRYPOINT [ "/website_bootcommand.sh" ]

EXPOSE 8000

