# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-03-15 10:59
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('divesites', '0021_auto_20160315_1057'),
    ]

    operations = [
        migrations.RenameField(
            model_name='divesite',
            old_name='bottom_type',
            new_name='seabed',
        ),
    ]
