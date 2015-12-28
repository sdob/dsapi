from __future__ import unicode_literals

import uuid
from datetime import timedelta
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from dsapi.settings import AUTH_USER_MODEL
from .validators import validate_duration, validate_latitude, validate_longitude

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
    # Images are sorted out separately; we'll just store a URL
    header_image_url = models.URLField(blank=True)
    # Geographical coordinates
    latitude = models.DecimalField(max_digits=10, decimal_places=7, validators=[validate_latitude])
    longitude = models.DecimalField(max_digits=10, decimal_places=7, validators=[validate_longitude])
    # Creation metadata
    owner = models.ForeignKey(AUTH_USER_MODEL, related_name="divesites")
    creation_date = models.DateTimeField(auto_now_add=True)

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
    # Creation metadata
    creation_date = models.DateTimeField(auto_now_add=True)

    def clean(self):
        # For now we'll be explicit about validating
        # XXX: this logic is duplicated in the serializer. Need to think
        # about how to abstract it.
        validate_duration(self.duration)
        if self.start_time + self.duration >= timezone.now():
            raise ValidationError(_('Dive must have taken place in the past'))
        return super(Dive, self).clean()

    def save(self, *args, **kwargs):
        self.clean()
        super(Dive, self).save(*args, **kwargs)
