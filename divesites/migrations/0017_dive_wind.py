# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-03-13 17:36
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('divesites', '0016_divesite_bottom_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='dive',
            name='wind',
            field=models.SmallIntegerField(blank=True, choices=[(0, 'Calm'), (1, 'Light air'), (2, 'Light breeze'), (3, 'Gentle breeze'), (4, 'Moderate breeze'), (5, 'Fresh breeze'), (6, 'Strong breeze'), (7, 'High wind'), (8, 'Gale'), (9, 'Strong gale'), (10, 'Storm'), (11, 'Violent storm'), (12, 'Hurricane')], null=True),
        ),
    ]