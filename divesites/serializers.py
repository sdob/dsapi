from datetime import timedelta
from django.utils import timezone
from rest_framework import serializers
from profiles.serializers import ProfileSerializer
from profiles.models import Profile
from divesites.models import Dive, Divesite
from . import models
from . import validators


class DiveSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Dive
        depth = 1
        #'fields = ('diver', 'id', 'depth', 'duration', 'divesite',)
    diver = ProfileSerializer(source='diver.profile', read_only=True)

    def validate(self, attrs):
        # If we're doing a partial update, then only one (or neither)
        # of these fields may be available in the data passed in to
        # the validate method. For some reason this failed using the
        # usual attrs.get(key, default) pattern (which raises an
        # AttributeError, no idea why).
        if 'start_time' in attrs.keys():
            start_time = attrs['start_time']
        else:
            start_time = self.instance.start_time
        if 'duration' in attrs.keys():
            duration = attrs['duration']
        else:
            duration  = self.instance.duration

        # Validate duration
        if duration <= timedelta(seconds=0):
            raise serializers.ValidationError('duration must be greater than 0')
        # Validate start_time + duration so that dives begin and end in the past
        if start_time >= timezone.now():
            raise serializers.ValidationError('dive must have started in the past')
        if start_time + duration >= timezone.now():
            raise serializers.ValidationError('dive must have ended in the past')
        return attrs


class DivesiteSerializer(serializers.ModelSerializer):
    """Serialize everything we know about a Divesite."""
    class Meta:
        model = models.Divesite
        depth = 1
        fields = ('owner', 'depth', 'dives', 'name', 'id', 'latitude', 'longitude', 'level', 'boat_entry', 'shore_entry','dives', )
    depth = serializers.ReadOnlyField(source='get_average_maximum_depth')
    owner = ProfileSerializer(source='owner.profile', read_only=True)

    def validate(self, attrs):
        if 'boat_entry' in attrs.keys():
            boat_entry = attrs['boat_entry']
        else:
            boat_entry = self.instance.boat_entry
        if 'shore_entry' in attrs.keys():
            shore_entry = attrs['shore_entry']
        else:
            shore_entry = self.instance.shore_entry
        # At least one of [boat_entry, shore_entry] must be true;
        # otherwise the site is inaccessible
        if not (boat_entry or shore_entry):
            raise serializers.ValidationError('either boat_entry or shore_entry must be true')
        return attrs
