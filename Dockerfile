# vim: set ft=conf
FROM python:2.7

ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH /app

RUN mkdir /app
WORKDIR /app

RUN apt-get update -qq && apt-get install -y mysql-client netcat

ADD requirements/ /app/requirements
ADD requirements.txt /app/
RUN pip install -r requirements.txt

ADD wait-for-mysqld.sh /wait-for-mysqld.sh
ADD appstart.sh /appstart.sh
