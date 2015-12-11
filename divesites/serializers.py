from rest_framework import serializers
from . import models
from profiles.serializers import ProfileSerializer

class DiveSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Dive
    diver = ProfileSerializer(source='diver.profile', read_only=True)


class CompactDiveSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Dive
        fields = ('depth', 'duration',)
    diver = ProfileSerializer(source='diver.profile', read_only=True)


class DivesiteSerializer(serializers.ModelSerializer):
    """Serialize everything we know about a Divesite."""
    class Meta:
        model = models.Divesite
        fields = ('owner', 'depth', 'dives', 'name', 'id', 'latitude', 'longitude', 'level', 'boat_entry', 'shore_entry','dives', )
    depth = serializers.ReadOnlyField(source='get_average_maximum_depth')
    dives = DiveSerializer(many=True, read_only=True)
    owner = ProfileSerializer(source='owner.profile', read_only=True)


class CompactDivesiteSerializer(serializers.ModelSerializer):
    """Serialize a subset of a Divesite's fields (so that lists don't become overlong)."""
    class Meta:
        model = models.Divesite
        fields = ('id', 'latitude', 'longitude', 'level', 'depth', 'boat_entry', 'shore_entry', 'owner',)
    depth = serializers.ReadOnlyField(source='get_average_maximum_depth')
    owner = ProfileSerializer(source='owner.profile', read_only=True)
