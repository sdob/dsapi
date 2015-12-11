from __future__ import unicode_literals

import uuid
from datetime import timedelta
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from dsapi.settings import AUTH_USER_MODEL
import numpy as np
#from profiles.models import Profile

def validate_duration(value):
    if value <= timedelta(seconds=0):
        raise ValidationError('%s is not a valid duration' % value)

def validate_latitude(value):
    if not -90 <= value <= 90:
        raise ValidationError('%s is not a valid latitude' % value)

def validate_longitude(value):
    if not -180 <= value <= 180:
        raise ValidationError('%s is not a valid longitude' % value)

class Divesite(models.Model):

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
    # TODO: eventually, we'll extract this information from logged dives rather than
    # have a single field on the Divesite model
    def get_average_maximum_depth(self):
        if self.dives.all():
            return np.mean([_.depth for _ in self.dives.all()])
        return 0
    # Images are sorted out separately; we'll just store a URL
    header_image_url = models.URLField(blank=True)
    # Geographical coordinates
    latitude = models.DecimalField(max_digits=10, decimal_places=7, validators=[validate_latitude])
    longitude = models.DecimalField(max_digits=10, decimal_places=7, validators=[validate_longitude])
    # Creation metadata
    owner = models.ForeignKey(AUTH_USER_MODEL, related_name="divesites")
    #creation_date = models.DateTimeField(auto_add=True)

    def _get_profile(self):
        return self.owner.profile

    def clean(self):
        validate_latitude(self.latitude)
        validate_longitude(self.longitude)
        super(Divesite, self).clean()

    def save(self, *args, **kwargs):
        self.clean()
        super(Divesite, self).save(*args, **kwargs)


class Dive(models.Model):
    class Meta:
        ordering = ['start_time']

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    comment = models.TextField(blank=True)
    depth = models.DecimalField(max_digits=4, decimal_places=1)
    divesite = models.ForeignKey(Divesite, related_name="dives")
    diver = models.ForeignKey(AUTH_USER_MODEL, related_name="dives")
    duration = models.DurationField() # TODO: Must be greater than 0
    start_time = models.DateTimeField() # TODO: Must be in the past (i.e., date + duration < now)

    def _get_profile(self):
        return self.diver.profile

    def clean(self):
        # For now we'll be explicit about validating
        validate_duration(self.duration)
        if self.start_time + self.duration >= timezone.now():
            raise ValidationError(_('Dive must have taken place in the past'))
        super(Dive, self).clean()

    def save(self, *args, **kwargs):
        self.clean()
        super(Dive, self).save(*args, **kwargs)
