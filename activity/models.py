from __future__ import unicode_literals

from django.db import models

from django.utils import timezone
from divesites.models import Dive, Divesite
from dsapi.settings import AUTH_USER_MODEL
from model_utils.managers import InheritanceManager

class Activity(models.Model):

    #class Meta:
        #abstract = True

    objects = InheritanceManager()

    user = models.ForeignKey(AUTH_USER_MODEL)
    desc = models.TextField(blank=True)
    creation_date = models.DateTimeField(default=timezone.now)


class DivesiteCreation(Activity):
    divesite = models.ForeignKey(Divesite)


class DiveLog(Activity):
    dive = models.ForeignKey(Dive)


# Post-creation signal to create a DivesiteCreation object
from django.db.models.signals import post_save
def create_divesite_creation(sender, **kwargs):
    divesite = kwargs['instance']
    if kwargs['created']:
        user = divesite.owner
        activity = DivesiteCreation(user=user, divesite=divesite)
        activity.save()
post_save.connect(create_divesite_creation, sender=Divesite)

# Post-creation signal to create a DiveLog object
from django.db.models.signals import post_save
def create_dive_log(sender, **kwargs):
    dive = kwargs['instance']
    if kwargs['created']:
        user = dive.diver
        activity = DiveLog(user=user, dive=dive)
        activity.save()
post_save.connect(create_dive_log, sender=Dive)
