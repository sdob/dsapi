# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-02-15 23:45
from __future__ import unicode_literals

from actstream import action
from actstream.models import Action
from django.db import migrations

class Migration(migrations.Migration):

    def create_actions(apps, schema_editor):
        Dive = apps.get_model('divesites', 'Dive')
        Divesite = apps.get_model('divesites', 'Divesite')
        Slipway = apps.get_model('divesites', 'Slipway')
        Compressor = apps.get_model('divesites', 'Compressor')
        DivesiteComment = apps.get_model('comments', 'DivesiteComment')
        CompressorComment = apps.get_model('comments', 'CompressorComment')
        SlipwayComment = apps.get_model('comments', 'SlipwayComment')
        # Create Action items for Divesites
        for divesite in Divesite.objects.all():
            if not Action.objects.filter(target_object_id=divesite.id).exists():
                user = divesite.owner
                Action.objects.create(actor=user, verb='created', target=divesite)

        # Create Action items for Compressors
        for compressor in Compressor.objects.all():
            if not Action.objects.filter(target_object_id=compressor.id).exists():
                user = compressor.owner
                Action.objects.create(actor=user, verb='created', target=compressor)

        # Create Action items for Slipways
        for slipway in Slipway.objects.all():
            if not Action.objects.filter(target_object_id=slipway.id).exists():
                user = slipway.owner
                Action.objects.create(actor=user, verb='created', target=slipway)

        # Create Action items for Dives
        for dive in Dive.objects.all():
            if not Action.objects.filter(action_object_object_id=dive.id).exists():
                user = dive.diver
                divesite = dive.divesite
                Action.objects.create(actor=user, verb='logged a dive at',
                        action_object=dive, target=divesite)
        # Create Action items for Compressor comments
        for comment in CompressorComment.objects.all():
            if not Action.objects.filter(action_object_object_id=comment.id).exists():
                user = comment.owner
                compressor = comment.compressor
                Action.objects.create(actor=user, verb='commented on',
                        action_object=comment, target=compressor)
        # Create Action items for Divesite comments
        for comment in DivesiteComment.objects.all():
            if not Action.objects.filter(action_object_object_id=comment.id).exists():
                user = comment.owner
                divesite = comment.divesite
                Action.objects.create(actor=user, verb='commented on',
                        action_object=comment, target=divesite)
        # Create Action items for Slipway comments
        for comment in SlipwayComment.objects.all():
            if not Action.objects.filter(action_object_object_id=comment.id).exists():
                user = comment.owner
                slipway = comment.slipway
                Action.objects.create(actor=user, verb='commented on',
                        action_object=comment, target=slipway)

    
    def rollback(apps, schema_editor):
        # Just kill all existing Action objects
        Action.objects.all().delete()

    dependencies = [
        ('divesites', '0009_auto_20160208_1546'),
    ]

    operations = [
            migrations.RunPython(create_actions, rollback)
    ]