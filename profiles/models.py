from __future__ import unicode_literals

from datetime import timedelta
from django.db import models
from django.utils import timezone
from dsapi.settings import AUTH_USER_MODEL as User
from divesites.models import Dive

# Create your models here.
class Profile(models.Model):
    # One-to-one mapping to an authentication User model
    user = models.OneToOneField(User)
    # The user's name
    name = models.CharField(max_length=200)
    # Some stats
    def get_hours_underwater(self):
        return sum([_.duration.total_seconds() for _ in self.user.dives.all()]) // (3600)
    def get_number_of_divesites_visited(self):
        return len(set([_.divesite for _ in self.user.dives.all()]))
    def count_dives_in_last_365_days(self):
        return Dive.objects.filter(diver=self.user, start_time__date__gte=timezone.now() - timedelta(days=365)).count()
    def count_dives_in_last_90_days(self):
        return Dive.objects.filter(diver=self.user, start_time__date__gte=timezone.now() - timedelta(days=90)).count()


# Post-save signal to create a Profile
from django.db.models.signals import post_save
def create_profile(sender, **kwargs):
    user = kwargs['instance']
    if kwargs['created']:
        profile = Profile(user=user)
        profile.save()
post_save.connect(create_profile, sender=User)
