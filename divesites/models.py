import uuid
import urllib.request
import urllib.error
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from dsapi.settings import GOOGLE_REVERSE_GEOCODING_URL_STRING_TEMPLATE
from .validators import validate_duration, validate_latitude, validate_longitude

def retrieve_geocoding_data(lat, lng):
        try:
            url = GOOGLE_REVERSE_GEOCODING_URL_STRING_TEMPLATE % (lat, lng)
            reverse_geocoding_json = urllib.request.urlopen(url).read()
            return reverse_geocoding_json
        except:
            # We might get a URLError or HTTPError, but there's really
            # nothing we can do about it except log it
            print('Error while retrieving geocoding JSON for %s' % self.name)
            return None


class Divesite(models.Model):

    def __str__(self):
        return self.name

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    # Site data for filtering
    boat_entry = models.BooleanField(default=True)
    shore_entry = models.BooleanField(default=True)
    level = models.SmallIntegerField(choices=(
        (0, 'Beginner',),
        (1, 'Intermediate',),
        (2, 'Advanced',),
        ))
    # For site depth, use the mean of the dives logged at this site, or
    # return 0 as a default if nobody's logged a dive here.
    def get_average_maximum_depth(self):
        if self.dives.all():
            dives = self.dives.all()
            return sum([_.depth for _ in dives]) / len(dives)
        return 0
    def get_average_duration(self):
        """Return average duration, in minutes"""
        if self.dives.all():
            dives = self.dives.all()
            return  sum([_.duration.total_seconds() for _ in dives]) // (60 * len(dives))
        return 0
    # Geographical coordinates
    latitude = models.DecimalField(max_digits=23, decimal_places=20, validators=[validate_latitude])
    longitude = models.DecimalField(max_digits=23, decimal_places=20, validators=[validate_longitude])
    # Country and administrative-area data; we'll use the Google reverse-geocoding API to retrieve
    # these (and store the JSON in a string in the db)
    geocoding_data = models.TextField(blank=True)
    # Creation metadata
    owner = models.ForeignKey(User, related_name="divesites")
    creation_date = models.DateTimeField(auto_now_add=True)

    def clean(self):
        validate_latitude(self.latitude)
        validate_longitude(self.longitude)
        super(Divesite, self).clean()

    def save(self, *args, **kwargs):
        self.clean()
        # OK, so now the model is OK; let's retrieve geocoding data from Google
        geocoding_data = retrieve_geocoding_data(self.latitude, self.longitude)
        if geocoding_data:
            self.geocoding_data = geocoding_data
        super(Divesite, self).save(*args, **kwargs)


class Dive(models.Model):
    class Meta:
        ordering = ['date', 'time']

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    comment = models.TextField(blank=True)
    depth = models.DecimalField(max_digits=4, decimal_places=1)
    divesite = models.ForeignKey(Divesite, related_name="dives")
    diver = models.ForeignKey(User, related_name="dives")
    duration = models.DurationField() # TODO: Must be greater than 0
    # Date and time of dive are separate fields
    date = models.DateField()
    time = models.TimeField(blank=True, null=True)
    # Creation metadata
    creation_date = models.DateTimeField(auto_now_add=True)

    def clean(self):
        return super(Dive, self).clean()

    def save(self, *args, **kwargs):
        self.clean()
        super(Dive, self).save(*args, **kwargs)


class Compressor(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    # Geographical coordinates
    latitude = models.DecimalField(max_digits=23, decimal_places=20, validators=[validate_latitude])
    longitude = models.DecimalField(max_digits=23, decimal_places=20, validators=[validate_longitude])
    # Creation metadata
    owner = models.ForeignKey(User, related_name='compressors')
    creation_data = models.DateTimeField(auto_now_add=True)
    # Geocoding data
    geocoding_data = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        # Try to retrieve geocoding data from Google
        geocoding_data = retrieve_geocoding_data(self.latitude, self.longitude)
        if geocoding_data:
            self.geocoding_data = geocoding_data
        super(Compressor, self).save(*args, **kwargs)


class Slipway(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    # Geographical coordinates
    latitude = models.DecimalField(max_digits=23, decimal_places=20, validators=[validate_latitude])
    longitude = models.DecimalField(max_digits=23, decimal_places=20, validators=[validate_longitude])
    # Creation metadata
    owner = models.ForeignKey(User, related_name='slipways')
    creation_data = models.DateTimeField(auto_now_add=True)
    # Geocoding data
    geocoding_data = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        # Try to retrieve geocoding data from Google
        geocoding_data = retrieve_geocoding_data(self.latitude, self.longitude)
        if geocoding_data:
            self.geocoding_data = geocoding_data
        super(Slipway, self).save(*args, **kwargs)
