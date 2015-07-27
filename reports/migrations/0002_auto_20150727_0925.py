# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='category',
            options={'verbose_name_plural': 'categories', 'ordering': ['order']},
        ),
        migrations.AlterModelOptions(
            name='projectcategory',
            options={'verbose_name_plural': 'project categories'},
        ),
    ]
