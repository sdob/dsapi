from rest_framework import serializers
from activity.models import Activity, DiveLog, DivesiteCreation
from divesites.models import Dive, Divesite
from divesites.serializers import DiveSerializer
from profiles.models import Profile
from profiles.serializers import ProfileSerializer


class CompactProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ('id', 'name',)


class DivesiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Divesite
        fields = ('id', 'name', 'owner', 'latitude', 'longitude',)
    owner = CompactProfileSerializer(source='owner.profile')


class DiveLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiveLog
        fields = ('user', 'id', 'creation_date','dive',)
    user = CompactProfileSerializer(source='user.profile')
    dive = DiveSerializer()


class DivesiteCreationSerializer(serializers.ModelSerializer):
    class Meta:
        model = DivesiteCreation
        fields = ('user', 'id', 'creation_date','divesite',)
    user = CompactProfileSerializer(source='user.profile')
    divesite = DivesiteSerializer()


def serializer_factory(obj):
    # Loosely based on the solution here:
    # http://stackoverflow.com/questions/33137165/django-rest-framework-abstract-class-serializer
    if isinstance(obj, DiveLog):
        return DiveLogSerializer
    if isinstance(obj, DivesiteCreation):
        return DivesiteCreationSerializer
