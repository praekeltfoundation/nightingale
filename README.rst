nightingale
=======================================

A light for those in need and a generic reporting tool.

Setup
---------------------------------------

Remember to enable hbase on your postgres template
::
    psql -d template1 -c 'create extension hstore;'

If you want to use docker-compose here's some boilerplate
::
    nginxproxy:
      restart: always
      image: jwilder/nginx-proxy
      volumes:
        - /var/run/docker.sock:/tmp/docker.sock:ro
      ports:
        - "80:80"

    nightingale:
      restart: always
      build: ./
      expose:
        - "8001"
      links:
        - nightingaledb:nightingaledb
      env_file: nightingale.env
      command: /usr/local/bin/gunicorn nightingale.wsgi:application -w 2 -b :8001

    nightingaledb:
      restart: always
      image: aidanlister/postgres-hstore:latest
      volumes_from:
        - nightingaledbdata
      ports:
        - "5433:5432"

    nightingaledbdata:
      restart: no
      image: aidanlister/postgres-hstore:latest
      volumes:
        - /var/lib/postgresql
      command: true

    nightingalecelery:
      restart: always
      build: ./
      links:
        - nightingaledb:nightingaledb
        - nightingaleredis:nightingaleredis
      env_file: nightingale.env
      command: /usr/local/bin/python manage.py celery worker --loglevel=info

    nightingalecelerybeat:
      restart: always
      build: ./
      links:
        - nightingaledb:nightingaledb
        - nightingaleredis:nightingaleredis
      env_file: nightingale.env
      command: /usr/local/bin/python manage.py celery beat --loglevel=info

    nightingaleredis:
      restart: always
      image: redis:latest
      ports:
        - "6379:6379"

And the nightingale.env
::
    VIRTUAL_HOST=nightingale.local,nightingale.praekelt.com
    SECRET_KEY=stuffandnonsense
    NIGHTINGALE_DATABASE=postgres://postgres:@nightingaledb/postgres
    DEBUG=True
    NIGHTINGALE_DSN=https://replaceme
    NIGHTINGALE_REDIS=redis://nightingaleredis:6379/0
