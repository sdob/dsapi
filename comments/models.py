from actstream import action
from actstream.models import Action
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from divesites.models import Divesite, Compressor, Slipway

# Create your models here.
class Comment(models.Model):
    owner = models.ForeignKey(User, related_name="comments")
    text = models.TextField()
    creation_date = models.DateTimeField(auto_now_add=True, null=True)


class DivesiteComment(Comment):
    divesite = models.ForeignKey(Divesite, related_name="comments")


class SlipwayComment(Comment):
    slipway = models.ForeignKey(Slipway, related_name="comments")


class CompressorComment(Comment):
    compressor = models.ForeignKey(Compressor, related_name="comments")


def send_divesite_comment_creation_action(sender, instance, created, **kwargs):
    if created:
        verb = 'commented'
        action.send(instance.owner, verb=verb, action_object=instance, target=instance.divesite)
post_save.connect(send_divesite_comment_creation_action, sender=DivesiteComment)

def send_slipway_comment_creation_action(sender, instance, created, **kwargs):
    if created:
        verb = 'commented'
        action.send(instance.owner, verb=verb, action_object=instance, target=instance.slipway)
post_save.connect(send_slipway_comment_creation_action, sender=SlipwayComment)

def send_compressor_comment_creation_action(sender, instance, created, **kwargs):
    if created:
        verb = 'commented'
        action.send(instance.owner, verb=verb, action_object=instance, target=instance.compressor)
post_save.connect(send_compressor_comment_creation_action, sender=CompressorComment)
