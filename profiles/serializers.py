from rest_framework import serializers
from .models import Profile
from divesites.models import Dive, Divesite

class UnattributedDivesiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Divesite
        fields = ('id', 'name', 'description',
                'boat_entry', 'shore_entry', 'level',
                'latitude', 'longitude',)

class UnattributedDiveSerializer(serializers.ModelSerializer):
    # This isn't a great idea, but it gets us around the problem of
    # circular imports in Python (we can't import DiveSerializer
    # in here if we're importing ProfileSerializer there).
    # FIXME: There's a better way to do this, but I'll need to work
    # out what.
    class Meta:
        model = Dive
        fields = ('id', 'depth', 'duration', 'comment', 'start_time', 'divesite',)
    divesite = UnattributedDivesiteSerializer()

class MinimalProfileSerializer(serializers.ModelSerializer):
    # a Profile serializer that just provides ID and name fields
    class Meta:
        model = Profile
        fields = ('id', 'name',)


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
    dives = UnattributedDiveSerializer(source='user.dives', many=True, read_only=True)
    divesites = UnattributedDivesiteSerializer(source='user.divesites', many=True, read_only=True)
    date_joined = serializers.ReadOnlyField(source='user.date_joined', read_only=True)
    hours_underwater = serializers.ReadOnlyField(source='get_hours_underwater')
    divesites_visited = serializers.ReadOnlyField(source='get_number_of_divesites_visited');
    dives_in_last_365_days = serializers.ReadOnlyField(source='count_dives_in_last_365_days');
    dives_in_last_90_days = serializers.ReadOnlyField(source='count_dives_in_last_90_days');
