# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-02-08 15:46
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('divesites', '0008_auto_20160208_1131'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dive',
            name='time',
            field=models.TimeField(blank=True, null=True),
        ),
    ]
