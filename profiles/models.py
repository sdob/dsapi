import uuid

from datetime import timedelta
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from divesites.models import Dive

# Create your models here.
class Profile(models.Model):
    def __str__(self):
        return self.name
    # ID is a UUID
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # One-to-one mapping to an authentication User model
    user = models.OneToOneField(User)
    # The user's name
    name = models.CharField(max_length=200)
    # An arbitrary text field containing bio data, etc.
    about_me = models.TextField(blank=True)

    # Users this user follows
    follow_targets = models.ManyToManyField('self', related_name='followers', symmetrical=False)

    # Some stats
    def get_hours_underwater(self):
        return sum([_.duration.total_seconds() for _ in self.user.dives.all()]) // (3600)
    def get_number_of_divesites_visited(self):
        return len(set([_.divesite for _ in self.user.dives.all()]))
    def count_dives_in_last_365_days(self):
        return Dive.objects.filter(diver=self.user, date__gte=timezone.now() - timedelta(days=365)).count()
    def count_dives_in_last_90_days(self):
        return Dive.objects.filter(diver=self.user, date__gte=timezone.now() - timedelta(days=90)).count()


# Post-save signal to create a Profile
from django.db.models.signals import post_save
def create_profile(sender, **kwargs):
    user = kwargs['instance']
    if kwargs['created']:
        profile = Profile(user=user)
        # If the user object was populated on creation with first and
        # last names (e.g., through social account login), then
        # automatically set the profile's name attribute
        if user.first_name and user.last_name:
            profile.name = ' '.join([user.first_name, user.last_name])
        profile.save()
post_save.connect(create_profile, sender=User)
