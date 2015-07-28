# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.gis.db.models.fields
import django.contrib.postgres.fields.hstore


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
        ('reports', '0002_auto_20150727_0925'),
    ]

    operations = [
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('point', django.contrib.gis.db.models.fields.PointField(srid=4326)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Report',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('contact_key', models.CharField(max_length=36)),
                ('to_addr', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True, null=True)),
                ('incident_at', models.DateTimeField(null=True)),
                ('metadata', django.contrib.postgres.fields.hstore.HStoreField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('category', models.ForeignKey(to='reports.Category', related_name='reports')),
                ('location', models.ForeignKey(to='reports.Location', related_name='reports')),
                ('project', models.ForeignKey(to='accounts.Project', related_name='reports')),
            ],
        ),
    ]
