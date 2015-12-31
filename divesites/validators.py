from datetime import timedelta
from django.core.exceptions import ValidationError

def validate_duration(value):
    if value <= timedelta(seconds=0):
        raise ValidationError('%s is not a valid duration' % value)

def validate_latitude(value):
    if not -90 <= value <= 90:
        raise ValidationError('%s is not a valid latitude' % value)

def validate_longitude(value):
    if not -180 <= value <= 180:
        raise ValidationError('%s is not a valid longitude' % value)

