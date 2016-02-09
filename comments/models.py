from django.contrib.auth.models import User
from django.db import models
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
