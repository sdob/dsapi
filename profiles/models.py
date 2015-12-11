from __future__ import unicode_literals

from django.db import models
from dsapi.settings import AUTH_USER_MODEL as User

# Create your models here.
class Profile(models.Model):
    # One-to-one mapping to an authentication User model
    user = models.OneToOneField(User)
    # The user's name
    name = models.CharField(max_length=200)
    pass

# Post-save signal to create a Profile
from django.db.models.signals import post_save
def create_profile(sender, **kwargs):
    user = kwargs['instance']
    if kwargs['created']:
        profile = Profile(user=user)
        profile.save()
post_save.connect(create_profile, sender=User)
