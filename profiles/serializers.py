from rest_framework import serializers
from .models import Profile
from divesites.models import Dive, Divesite

class UnattributedDivesiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Divesite
        fields = ('id', 'name', 'description',
                'boat_entry', 'shore_entry', 'level', 'header_image_url',
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


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        depth = 1
        #fields = ('id', 'name', 'dives',)
    dives = UnattributedDiveSerializer(source='user.dives', many=True, read_only=True)
    divesites = UnattributedDivesiteSerializer(source='user.divesites', many=True, read_only=True)
    date_joined = serializers.ReadOnlyField(source='user.date_joined', read_only=True)
