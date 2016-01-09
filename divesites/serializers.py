from datetime import timedelta
from urlparse import urlparse
from django.utils import timezone
from rest_framework import serializers
from profiles.serializers import MinimalProfileSerializer, ProfileSerializer
from profiles.models import Profile
from divesites.models import Dive, Divesite
from . import models
from . import validators

class DivesiteDistanceValidator(object):

    def __init__(self, queryset):
        self.queryset = queryset

    def set_context(self, serializer):
        self.instance = getattr(serializer, 'instance', None)

    def enforce_required_fields(self, attrs):
        pass # TODO

    def exclude_current_instance(self, attrs, queryset):
        """If an instance is being updated, ignore it."""
        if self.instance is not None:
            return queryset.exclude(id=self.instance.id)
        return queryset

    def __call__(self, attrs):
        from decimal import Decimal
        # XXX: very shaky
        JUST_OVER_100_M_IN_DEGREES = Decimal(0.001)
        self.enforce_required_fields(attrs)
        if 'latitude' in attrs.keys():
            latitude = attrs['latitude']
        else:
            latitude = self.instance.latitude
        if 'longitude' in attrs.keys():
            longitude = attrs['longitude']
        else:
            longitude = self.instance.longitude
        queryset = self.queryset
        queryset = self.exclude_current_instance(attrs, queryset)
        # Filter on latitude value
        queryset = queryset.filter(latitude__gte=latitude-JUST_OVER_100_M_IN_DEGREES)
        queryset = queryset.filter(latitude__lte=latitude+JUST_OVER_100_M_IN_DEGREES)
        # Filter on longitude value
        queryset = queryset.filter(longitude__gte=longitude-JUST_OVER_100_M_IN_DEGREES)
        queryset = queryset.filter(longitude__lte=longitude+JUST_OVER_100_M_IN_DEGREES)
        if queryset.exists():
            raise serializers.ValidationError('Too close to an existing divesite')


class DiveListSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Dive
    diver = MinimalProfileSerializer(source='diver.profile', read_only=True)
    #diver = serializers.ReadOnlyField(source='diver.profile.id')
    #diver = ProfileSerializer(source='diver.profile', read_only=True)
    divesite = serializers.PrimaryKeyRelatedField(read_only=True)


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


class DivesiteListSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Divesite
        fields = ('id', 'depth', 'duration', 'level', 'boat_entry', 'shore_entry', 'latitude', 'longitude',)
    depth = serializers.ReadOnlyField(source='get_average_maximum_depth')
    duration = serializers.ReadOnlyField(source='get_average_duration')


class DivesiteSerializer(serializers.ModelSerializer):
    """Serialize everything we know about a Divesite."""
    class Meta:
        model = models.Divesite
        depth = 1
        fields = ('owner', 'depth', 'duration', 'dives', 'name', 'id',
                'latitude', 'longitude', 'level', 'boat_entry', 'shore_entry','dives',
                )
        validators = [
                DivesiteDistanceValidator(queryset=Divesite.objects.all())
                ]

    dives = DiveListSerializer(many=True, read_only=True)
    depth = serializers.ReadOnlyField(source='get_average_maximum_depth')
    duration = serializers.ReadOnlyField(source="get_average_duration")
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

