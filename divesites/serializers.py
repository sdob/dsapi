from rest_framework import serializers
from . import models
from profiles.serializers import ProfileSerializer
from profiles.models import Profile
from divesites.models import Dive, Divesite


class DiveSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Dive
        depth = 1
        #'fields = ('diver', 'id', 'depth', 'duration', 'divesite',)
    diver = ProfileSerializer(source='diver.profile', read_only=True)


class DivesiteSerializer(serializers.ModelSerializer):
    """Serialize everything we know about a Divesite."""
    class Meta:
        model = models.Divesite
        depth = 1
        fields = ('owner', 'depth', 'dives', 'name', 'id', 'latitude', 'longitude', 'level', 'boat_entry', 'shore_entry','dives', )
    depth = serializers.ReadOnlyField(source='get_average_maximum_depth')
    owner = ProfileSerializer(source='owner.profile', read_only=True)
