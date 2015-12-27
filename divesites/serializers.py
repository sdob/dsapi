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

        if start_time + duration >= timezone.now():
            raise serializers.ValidationError('dive must have started and finished in the past')
        return attrs


class DivesiteSerializer(serializers.ModelSerializer):
    """Serialize everything we know about a Divesite."""
    class Meta:
        model = models.Divesite
        depth = 1
        fields = ('owner', 'depth', 'dives', 'name', 'id', 'latitude', 'longitude', 'level', 'boat_entry', 'shore_entry','dives', )
    depth = serializers.ReadOnlyField(source='get_average_maximum_depth')
    owner = ProfileSerializer(source='owner.profile', read_only=True)
