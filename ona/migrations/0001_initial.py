# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.postgres.fields.hstore


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_integration'),
        ('reports', '0006_auto_20150804_1932'),
    ]

    operations = [
        migrations.CreateModel(
            name='Submission',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('content', models.TextField()),
                ('metadata', django.contrib.postgres.fields.hstore.HStoreField(default={}, null=True, blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('integration', models.ForeignKey(related_name='submissions', to='accounts.Integration')),
                ('report', models.ForeignKey(related_name='submissions', to='reports.Report', null=True)),
            ],
        ),
    ]
