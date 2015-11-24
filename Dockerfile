# vim: set ft=conf
FROM python:2.7

ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH /app

RUN mkdir /app
WORKDIR /app

ADD requirements/ /app/requirements
ADD requirements.txt /app/
RUN pip install -r requirements.txt

CMD python manage.py migrate --noinput && \
    python manage.py runserver 0.0.0.0:80
