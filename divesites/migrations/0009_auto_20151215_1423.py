# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2015-12-15 14:23
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('divesites', '0008_auto_20151214_1604'),
    ]

    operations = [
        migrations.AddField(
            model_name='divesite',
            name='description',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='dive',
            name='comment',
            field=models.TextField(blank=True),
        ),
    ]
