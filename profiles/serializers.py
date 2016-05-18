from actstream.models import Action
from rest_framework import serializers
from .models import Profile
from django.contrib.auth.models import User
from divesites.models import Compressor, Dive, Divesite, Slipway
from comments.models import CompressorComment, DivesiteComment, SlipwayComment
from images.serializers import UserProfileImageSerializer
#from comments.serializers import DivesiteCommentSerializer


# We need to define our own custom serializers for divesites models in
# here, because we can't import serializers from the divesites module
# (we're importing ProfileSerializer in there). This smells, but it's
# necessary because of the problem of circular imports in Python.

class UnattributedDivesiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Divesite
        fields = ('id', 'name', 'description', 'boat_entry', 'shore_entry',
                'level', 'latitude', 'longitude', 'creation_date', 'geocoding_data',)


class UnattributedCompressorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Compressor
        fields = ('id', 'description', 'latitude', 'longitude', 'name', 'creation_date',)


class UnattributedSlipwaySerializer(serializers.ModelSerializer):
    class Meta:
        model = Slipway
        fields = ('id', 'name', 'description', 'latitude', 'longitude', 'creation_date',)


class UnattributedDiveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dive
        fields = ('id', 'depth', 'duration', 'comment', 'date', 'time', 'divesite',
                'cylinder_capacity', 'pressure_in', 'pressure_out', 'gas_mix',
                'air_temperature', 'water_temperature',
                'weather', 'wind',
                )
    divesite = UnattributedDivesiteSerializer()


class MinimalProfileSerializer(serializers.ModelSerializer):
    # a Profile serializer that just provides ID and name fields
    class Meta:
        model = Profile
        fields = ('id', 'name', 'profile_image',)
    profile_image = UserProfileImageSerializer(source='user.profile_image', read_only=True)


class UnattributedCompressorCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompressorComment
        fields = ('compressor', 'text', 'creation_date',)
        Compressor = UnattributedCompressorSerializer()


class UnattributedDivesiteCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = DivesiteComment
        fields = ('divesite', 'text', 'creation_date',)
        divesite = UnattributedDivesiteSerializer()

class UnattributedSlipwayCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = SlipwayComment
        fields = ('slipway', 'text', 'creation_date',)
        divesite = UnattributedSlipwaySerializer()

class OwnProfileSerializer(serializers.ModelSerializer):
    """This serializer exposes an email address and certain other personally-identifying information,
    so use with care."""
    class Meta:
        model = Profile
        exclude = ('follow_targets', 'user',)
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
        exclude = ('follow_targets', 'user',)
    compressors = UnattributedCompressorSerializer(source='user.compressors', many=True, read_only=True)
    dives = UnattributedDiveSerializer(source='user.dives', many=True, read_only=True)
    dives_in_last_365_days = serializers.ReadOnlyField(source='count_dives_in_last_365_days');
    dives_in_last_90_days = serializers.ReadOnlyField(source='count_dives_in_last_90_days');
    divesites = UnattributedDivesiteSerializer(source='user.divesites', many=True, read_only=True)
    divesites_visited = serializers.ReadOnlyField(source='get_number_of_divesites_visited');
    date_joined = serializers.ReadOnlyField(source='user.date_joined', read_only=True)
    hours_underwater = serializers.ReadOnlyField(source='get_hours_underwater')


# Generic related field for django-activity-stream objects.
class GenericRelatedField(serializers.Field):
    def to_representation(self, value):
        if isinstance(value, Profile):
            return MinimalProfileSerializer(value).data
        if isinstance(value, User):
            data = MinimalProfileSerializer(value.profile).data
            return data
        if isinstance(value, Dive):
            return UnattributedDiveSerializer(value).data

        # Handle comments
        if isinstance(value, DivesiteComment):
            return UnattributedDivesiteCommentSerializer(value).data
        if isinstance(value, CompressorComment):
            return UnattributedCompressorCommentSerializer(value).data
        if isinstance(value, SlipwayComment):
            return UnattributedSlipwayCommentSerializer(value).data

        # Handle places
        if isinstance(value, Compressor):
            return UnattributedCompressorSerializer(value).data
        if isinstance(value, Divesite):
            return UnattributedDivesiteSerializer(value).data
        if isinstance(value, Slipway):
            return UnattributedSlipwaySerializer(value).data
        return str(value)


class ActionSerializer(serializers.ModelSerializer):
    # Serialize an activity-stream action. Based on:
    # http://davidmburke.com/2015/07/08/building-an-api-for-django-activity-stream-with-generic-foreign-keys/
    class Meta:
        model = Action
        fields = ('actor', 'target', 'action_object', 'timestamp', 'verb',
                'target_type', 'target_object_id',)
    actor = GenericRelatedField(read_only=True)
    target = GenericRelatedField(read_only=True)
    action_object = GenericRelatedField(read_only=True)
    target_type = serializers.ReadOnlyField(source='target_content_type.name')
