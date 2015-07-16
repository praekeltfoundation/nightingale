#!/bin/sh
export DATABASE_URL='postgres://postgres:@/test_nightingale'
export DJANGO_SETTINGS_MODULE="nightingale.testsettings"
./manage.py test "$@"
