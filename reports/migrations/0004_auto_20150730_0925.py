# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0003_location_report'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='report',
            name='category',
        ),
        migrations.AddField(
            model_name='report',
            name='categories',
            field=models.ManyToManyField(to='reports.Category'),
        ),
        migrations.AlterField(
            model_name='report',
            name='project',
            field=models.ForeignKey(to='accounts.Project', related_name='reports', null=True),
        ),
    ]
