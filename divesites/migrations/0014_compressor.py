# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-01-10 14:36
from __future__ import unicode_literals

import divesites.validators
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('divesites', '0013_slipway'),
    ]

    operations = [
        migrations.CreateModel(
            name='Compressor',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=200)),
                ('description', models.TextField(blank=True)),
                ('latitude', models.DecimalField(decimal_places=7, max_digits=10, validators=[divesites.validators.validate_latitude])),
                ('longitude', models.DecimalField(decimal_places=7, max_digits=10, validators=[divesites.validators.validate_longitude])),
                ('creation_data', models.DateTimeField(auto_now_add=True)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='compressors', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
