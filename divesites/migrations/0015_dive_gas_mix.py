# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-03-11 12:41
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('divesites', '0014_auto_20160311_1227'),
    ]

    operations = [
        migrations.AddField(
            model_name='dive',
            name='gas_mix',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True),
        ),
    ]