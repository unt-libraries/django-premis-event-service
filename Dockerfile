# vim: set ft=conf
FROM python:3.7-stretch

RUN echo "US/Central" > /etc/timezone
RUN dpkg-reconfigure -f noninteractive tzdata

ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH /app

RUN mkdir /app
WORKDIR /app

ADD Pipfile /app/
ADD Pipfile.lock /app/

RUN apt-get update -qq && apt-get install -y mysql-client netcat

RUN pip install -U pip setuptools
RUN pip install pipenv
RUN pipenv install --dev --system --deploy --ignore-pipfile

ADD wait-for-mysqld.sh /wait-for-mysqld.sh
ADD appstart.sh /appstart.sh
