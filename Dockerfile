# vim: set ft=conf
FROM python:3.9

RUN echo "US/Central" > /etc/timezone
RUN dpkg-reconfigure -f noninteractive tzdata

ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH /app

RUN apt-get update && apt-get install -y \
    gcc \
    libxml2-dev \
    libxslt1-dev \
    python3-dev \
    build-essential \
    default-mysql-client \
    netcat-openbsd \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . /app/

RUN pip install '.[test]'

