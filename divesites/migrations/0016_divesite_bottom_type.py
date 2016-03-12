# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-03-11 15:13
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('divesites', '0015_dive_gas_mix'),
    ]

    operations = [
        migrations.AddField(
            model_name='divesite',
            name='bottom_type',
            field=models.SmallIntegerField(blank=True, choices=[('Blds', 'Boulders'), ('Cl', 'Clay'), ('Co', 'Coral'), ('M', 'Mud'), ('Rk', 'Rocky'), ('S', 'Sand')], null=True),
        ),
    ]
