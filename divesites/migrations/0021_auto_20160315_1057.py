# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-03-15 10:57
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('divesites', '0020_auto_20160313_1753'),
    ]

    operations = [
        migrations.AlterField(
            model_name='divesite',
            name='bottom_type',
            field=models.CharField(blank=True, choices=[('Blds', 'Boulders'), ('Cl', 'Clay'), ('Co', 'Coral'), ('M', 'Mud'), ('Rk', 'Rocky'), ('S', 'Sand')], max_length=20, null=True),
        ),
    ]
