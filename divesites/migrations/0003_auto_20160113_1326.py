# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-01-13 13:26
from __future__ import unicode_literals

import divesites.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('divesites', '0002_auto_20160113_1325'),
    ]

    operations = [
        migrations.AlterField(
            model_name='compressor',
            name='latitude',
            field=models.DecimalField(decimal_places=12, max_digits=15, validators=[divesites.validators.validate_latitude]),
        ),
        migrations.AlterField(
            model_name='compressor',
            name='longitude',
            field=models.DecimalField(decimal_places=12, max_digits=15, validators=[divesites.validators.validate_longitude]),
        ),
        migrations.AlterField(
            model_name='slipway',
            name='latitude',
            field=models.DecimalField(decimal_places=12, max_digits=15, validators=[divesites.validators.validate_latitude]),
        ),
        migrations.AlterField(
            model_name='slipway',
            name='longitude',
            field=models.DecimalField(decimal_places=12, max_digits=15, validators=[divesites.validators.validate_longitude]),
        ),
    ]
