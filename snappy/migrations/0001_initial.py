# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.postgres.fields.hstore


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0005_auto_20150731_1630'),
        ('accounts', '0002_integration'),
    ]

    operations = [
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('target', models.CharField(choices=[('VUMI', 'Vumi'), ('SNAPPY', 'Snappy')], max_length=6)),
                ('message', models.TextField(verbose_name='Message')),
                ('contact_key', models.CharField(null=True, max_length=36, blank=True)),
                ('from_addr', models.CharField(null=True, max_length=255, blank=True)),
                ('to_addr', models.CharField(null=True, max_length=255, blank=True)),
                ('delivered', models.BooleanField(default=False)),
                ('metadata', django.contrib.postgres.fields.hstore.HStoreField(null=True, blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('integration', models.ForeignKey(to='accounts.Integration', related_name='messages')),
                ('report', models.ForeignKey(null=True, to='reports.Report', related_name='messages')),
            ],
        ),
    ]
