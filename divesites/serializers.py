from datetime import datetime, timedelta
import haversine
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


class DiveSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Dive
        fields = ('comment', 'diver', 'id', 'depth', 'duration', 'divesite',
                'date', 'time',
                'cylinder_capacity', 'pressure_in', 'pressure_out', 'gas_mix',
                'air_temperature', 'water_temperature',
                )
    # Provide at least ID and name attributes for the diver
    diver = MinimalProfileSerializer(source='diver.profile', read_only=True)

    def validate_date(self, date):
        # All we care about is that users can't log a dive in the future.
        if date > timezone.now().date():
            raise serializers.ValidationError('Dive must have started in the past.')
        return date

    def validate_duration(self, duration):
        if duration <= timedelta(seconds=0):
            raise serializers.ValidationError('Duration must be greater than 0.')
        return duration


class DiveListSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Dive
        fields = ('id', 'comment', 'depth', 'duration', 'date', 'time', 'divesite', 'diver',
                'air_temperature', 'water_temperature',)
    diver = MinimalProfileSerializer(source='diver.profile', read_only=True)
    divesite = serializers.PrimaryKeyRelatedField(read_only=True)


class DivesiteSerializer(serializers.ModelSerializer):
    """Serialize everything we know about a Divesite."""
    class Meta:
        model = models.Divesite
        fields = ('depth', 'duration', 'dives', 'name', 'id',
                'latitude', 'longitude', 'level', 'boat_entry', 'shore_entry',
                'bottom_type',
                'description',
                'owner',
                'geocoding_data',
                )
        validators = [
                DivesiteDistanceValidator(queryset=Divesite.objects.all())
                ]

    dives = DiveListSerializer(many=True, read_only=True)
    depth = serializers.ReadOnlyField(source='get_average_maximum_depth')
    duration = serializers.ReadOnlyField(source="get_average_duration")
    # When we're sending a divesite, we don't want to send a full serialized Profile instance
    owner = MinimalProfileSerializer(source='owner.profile', read_only=True)

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


class DivesiteListSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Divesite
        fields = ('id', 'depth', 'duration', 'geocoding_data', 'level',
                'boat_entry', 'shore_entry', 'boat_entry',
                'latitude', 'longitude', 'name', 'owner',)
    depth = serializers.ReadOnlyField(source='get_average_maximum_depth')
    duration = serializers.ReadOnlyField(source='get_average_duration')
    # Give a small amount of information about the owner
    owner = MinimalProfileSerializer(source='owner.profile', read_only=True)


class CompressorSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Compressor
    owner = MinimalProfileSerializer(source='owner.profile', read_only=True)


class SlipwaySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Slipway
    owner = MinimalProfileSerializer(source='owner.profile', read_only=True)
