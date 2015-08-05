# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.postgres.fields.hstore


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0005_auto_20150731_1630'),
    ]

    operations = [
        migrations.AlterField(
            model_name='report',
            name='metadata',
            field=django.contrib.postgres.fields.hstore.HStoreField(null=True, blank=True, default={}),
        ),
    ]
