# vim: set ft=conf

FROM python:2.7
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH /app
RUN apt-get update -qq && apt-get install -y python-mysqldb mysql-client
RUN mkdir /app
WORKDIR /app
RUN pip install tox && \
    pip install Django==1.6

ADD requirements.txt /app/
RUN pip install -r requirements.txt

CMD python manage.py syncdb --noinput && \
    python manage.py runserver 0.0.0.0:80
