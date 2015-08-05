# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import uuid
import django.contrib.postgres.fields.hstore


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Integration',
            fields=[
                ('id', models.UUIDField(serialize=False, default=uuid.uuid4, primary_key=True, editable=False)),
                ('integration_type', models.CharField(max_length=10, choices=[('Snappy', 'Snappy'), ('Ona', 'Ona'), ('Vumi', 'Vumi')])),
                ('details', django.contrib.postgres.fields.hstore.HStoreField(blank=True, null=True)),
                ('active', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('project', models.ForeignKey(related_name='integrations', to='accounts.Project')),
            ],
        ),
    ]
