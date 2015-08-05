# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0004_auto_20150730_0925'),
    ]

    operations = [
        migrations.AlterField(
            model_name='report',
            name='incident_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
