from rest_framework import serializers
from .models import Profile
from divesites.models import Compressor, Dive, Divesite, Slipway

# We need to define our own custom serializers for divesites models in
# here, because we can't import serializers from the divesites module
# (we're importing ProfileSerializer in there). This smells, but it's
# necessary because of the problem of circular imports in Python.

class UnattributedDivesiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Divesite
        fields = ('id', 'name', 'description', 'boat_entry', 'shore_entry',
                'level', 'latitude', 'longitude',)

class UnattributedCompressorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Compressor
        fields = ('id', 'description', 'latitude', 'longitude', 'name',)


class UnattributedSlipwaySerializer(serializers.ModelSerializer):
    class Meta:
        model = Slipway
        fields = ('id', 'name', 'description', 'latitude', 'longitude',)


class UnattributedDiveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dive
        fields = ('id', 'depth', 'duration', 'comment', 'start_time', 'divesite',)
    divesite = UnattributedDivesiteSerializer()


class MinimalProfileSerializer(serializers.ModelSerializer):
    # a Profile serializer that just provides ID and name fields
    class Meta:
        model = Profile
        fields = ('id', 'name',)


class OwnProfileSerializer(serializers.ModelSerializer):
    """This serializer exposes an email address and certain other personally-identifying information,
    so use with care."""
    class Meta:
        model = Profile
        exclude = ('user',)
    compressors = UnattributedCompressorSerializer(source='user.compressors', many=True, read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    dives = UnattributedDiveSerializer(source='user.dives', many=True, read_only=True)
    divesites = UnattributedDivesiteSerializer(source='user.divesites', many=True, read_only=True)
    date_joined = serializers.ReadOnlyField(source='user.date_joined', read_only=True)
    hours_underwater = serializers.ReadOnlyField(source='get_hours_underwater')
    divesites_visited = serializers.ReadOnlyField(source='get_number_of_divesites_visited');
    dives_in_last_365_days = serializers.ReadOnlyField(source='count_dives_in_last_365_days');
    dives_in_last_90_days = serializers.ReadOnlyField(source='count_dives_in_last_90_days');
    slipways = UnattributedSlipwaySerializer(source='user.slipways', many=True, read_only=True)

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
    compressors = UnattributedCompressorSerializer(source='user.compressors', many=True, read_only=True)
    dives = UnattributedDiveSerializer(source='user.dives', many=True, read_only=True)
    dives_in_last_365_days = serializers.ReadOnlyField(source='count_dives_in_last_365_days');
    dives_in_last_90_days = serializers.ReadOnlyField(source='count_dives_in_last_90_days');
    divesites = UnattributedDivesiteSerializer(source='user.divesites', many=True, read_only=True)
    divesites_visited = serializers.ReadOnlyField(source='get_number_of_divesites_visited');
    date_joined = serializers.ReadOnlyField(source='user.date_joined', read_only=True)
    hours_underwater = serializers.ReadOnlyField(source='get_hours_underwater')
