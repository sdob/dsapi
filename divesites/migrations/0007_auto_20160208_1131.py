# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-02-08 11:31
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('divesites', '0006_auto_20160208_1114'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dive',
            name='start_time',
            field=models.DateTimeField(blank=True),
        ),
    ]
