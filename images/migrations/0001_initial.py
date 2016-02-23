# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-02-23 17:50
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('divesites', '0011_auto_20160217_1808'),
    ]

    operations = [
        migrations.CreateModel(
            name='BaseImage',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('caption', models.TextField()),
                ('creation_date', models.DateTimeField(auto_now_add=True)),
                ('is_header_image', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='CompressorImage',
            fields=[
                ('baseimage_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='images.BaseImage')),
                ('compressor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='divesites.Compressor')),
            ],
            bases=('images.baseimage',),
        ),
        migrations.CreateModel(
            name='DivesiteImage',
            fields=[
                ('baseimage_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='images.BaseImage')),
                ('divesite', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='divesites.Divesite')),
            ],
            bases=('images.baseimage',),
        ),
        migrations.CreateModel(
            name='SlipwayImage',
            fields=[
                ('baseimage_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='images.BaseImage')),
                ('slipway', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='divesites.Slipway')),
            ],
            bases=('images.baseimage',),
        ),
        migrations.AddField(
            model_name='baseimage',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
