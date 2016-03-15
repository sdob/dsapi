import uuid
import urllib.request
import urllib.error
from actstream import action
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.postgres.fields import JSONField
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import post_save
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from dsapi.settings import GOOGLE_REVERSE_GEOCODING_URL_STRING_TEMPLATE
from .validators import validate_duration, validate_latitude, validate_longitude

def retrieve_geocoding_data(lat, lng):
    """
    Contact the Google reverse-geocoding API to retrieve geocoding
    data for this lat/lng pair.
    """
    try:
        url = GOOGLE_REVERSE_GEOCODING_URL_STRING_TEMPLATE % (lat, lng)
        reverse_geocoding_json = urllib.request.urlopen(url).read()
        return reverse_geocoding_json
    except:
        # We might get a URLError or HTTPError, but there's really
        # nothing we can do about it except log it
        return None


class Divesite(models.Model):

    BOULDERS = 'Blds'
    CLAY = 'Cl'
    CORAL = 'Co'
    MUD = 'M'
    ROCKY = 'Rk'
    SAND = 'S'

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

    # Other site data, not worth filtering on
    seabed = models.CharField(choices=(
        (BOULDERS, 'Boulders'),
        (CLAY, 'Clay'),
        (CORAL, 'Coral'),
        (MUD, 'Mud'),
        (ROCKY, 'Rocky'),
        (SAND, 'Sand'),
        ),
        max_length=20,
        blank=True, null=True)
    # Geographical coordinates
    latitude = models.DecimalField(max_digits=23, decimal_places=20, validators=[validate_latitude])
    longitude = models.DecimalField(max_digits=23, decimal_places=20, validators=[validate_longitude])
    # Country and administrative-area data; we'll use the Google reverse-geocoding API to retrieve
    # these (and store the JSON in a string in the db)
    geocoding_data = models.TextField(blank=True)
    # Creation metadata
    owner = models.ForeignKey(User, related_name="divesites")
    creation_date = models.DateTimeField(auto_now_add=True)
    # images, through a generic relation
    images = GenericRelation('images.Image')

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

    # Cylinder size and pressure. We could do model-level checking that
    # these are non-negative, but that's for the future. Note that this
    # model assumes single-tank diving (or at least forces divers to do
    # the maths for multiple tanks...
    cylinder_capacity = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)
    pressure_in = models.IntegerField(blank=True, null=True)
    pressure_out = models.IntegerField(blank=True, null=True)

    # Conditions
    air_temperature = models.DecimalField(max_digits=4, decimal_places=1, blank=True, null=True)
    water_temperature = models.DecimalField(max_digits=4, decimal_places=1, blank=True, null=True)
    # Weather conditions are string-based
    weather = models.CharField(choices=(
        ('clear', 'Clear'),
        ('clouds', 'Clouds'),
        ('rain', 'Rain'),
        ('fog', 'Fog'),
        ('snow', 'Snow'),
        ),
        max_length=50,
        blank=True, null=True)
    # Wind values are Beaufort scale numbers
    wind = models.SmallIntegerField(choices=(
        (0, 'Calm'),
        (1, 'Light air'),
        (2, 'Light breeze'),
        (3, 'Gentle breeze'),
        (4, 'Moderate breeze'),
        (5, 'Fresh breeze'),
        (6, 'Strong breeze'),
        (7, 'High wind'),
        (8, 'Gale'),
        (9, 'Strong gale'),
        (10, 'Storm'),
        (11, 'Violent storm'),
        (12, 'Hurricane'),
        ), blank=True, null=True)

    # Gas mix --- this is implemented as JSON (since it could be air,
    # Nitrox, trimix, or potentially something more complex)
    gas_mix = JSONField(blank=True, null=True)

    def clean(self):
        return super(Dive, self).clean()

    def save(self, *args, **kwargs):
        self.clean()
        super(Dive, self).save(*args, **kwargs)


class Compressor(models.Model):
    def __str__(self):
        return self.name

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    # Geographical coordinates
    latitude = models.DecimalField(max_digits=23, decimal_places=20, validators=[validate_latitude])
    longitude = models.DecimalField(max_digits=23, decimal_places=20, validators=[validate_longitude])
    # Creation metadata
    owner = models.ForeignKey(User, related_name='compressors')
    creation_date = models.DateTimeField(auto_now_add=True)
    # Geocoding data
    geocoding_data = models.TextField(blank=True)

    # images, through a generic relation
    images = GenericRelation('images.Image')

    def save(self, *args, **kwargs):
        # Try to retrieve geocoding data from Google
        geocoding_data = retrieve_geocoding_data(self.latitude, self.longitude)
        if geocoding_data:
            self.geocoding_data = geocoding_data
        super(Compressor, self).save(*args, **kwargs)


class Slipway(models.Model):
    def __str__(self):
        return self.name

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    # Geographical coordinates
    latitude = models.DecimalField(max_digits=23, decimal_places=20, validators=[validate_latitude])
    longitude = models.DecimalField(max_digits=23, decimal_places=20, validators=[validate_longitude])
    # Creation metadata
    owner = models.ForeignKey(User, related_name='slipways')
    creation_date = models.DateTimeField(auto_now_add=True)
    # Geocoding data
    geocoding_data = models.TextField(blank=True)

    # images, through a generic relation
    images = GenericRelation('images.Image')

    def save(self, *args, **kwargs):
        # Try to retrieve geocoding data from Google
        geocoding_data = retrieve_geocoding_data(self.latitude, self.longitude)
        if geocoding_data:
            self.geocoding_data = geocoding_data
        super(Slipway, self).save(*args, **kwargs)


#
# Post-save signals
#

# When a user creates a site (a Compressor, Divesite, or Slipway), then
# generate a corresponding activity stream action.
def send_site_creation_action(sender, instance, created, **kwargs):
    if created:
        verb = 'created'
        # print('%s %s %s' % (instance.owner, verb, instance))
        action.send(instance.owner, verb='created', target=instance)
post_save.connect(send_site_creation_action, sender=Compressor)
post_save.connect(send_site_creation_action, sender=Divesite)
post_save.connect(send_site_creation_action, sender=Slipway)

# When a user logs a dive, then create a corresponding activity stream action.
def send_dive_creation_action(sender, instance, created, **kwargs):
    if created:
        verb = 'logged a dive at'
        # print('%s %s %s' % (instance.diver, verb, instance.divesite))
        action.send(instance.diver, verb='logged a dive', action_object=instance, target=instance.divesite)
post_save.connect(send_dive_creation_action, sender=Dive)
