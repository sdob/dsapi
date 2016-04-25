# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-04-06 15:08
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('divesites', '0022_auto_20160315_1059'),
    ]

    operations = [
        migrations.AddField(
            model_name='dive',
            name='average_depth',
            field=models.DecimalField(blank=True, decimal_places=1, max_digits=4, null=True),
        ),
    ]