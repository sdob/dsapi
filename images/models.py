import uuid
from cloudinary.models import CloudinaryField
from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from divesites.models import Compressor, Divesite, Slipway

class BaseImage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # Creation metadata
    owner = models.ForeignKey(User)
    caption = models.TextField(blank=True)
    image = CloudinaryField('image')
    creation_date = models.DateTimeField(auto_now_add=True)
    # Images can be assigned as the 'header image' of their site
    is_header_image = models.BooleanField(default=False)


class Image(models.Model):
    """
    This is an image that belongs to a thing (probably a site, since
    profile images are inherently different --- not content.
    """

    # Limit the number of possible content types that Images can have
    # as their foreign key
    limit_choices = \
            Q(app_label='divesites', model='compressor') | \
            Q(app_label='divesites', model='divesite') | \
            Q(app_label='divesites', model='slipway')

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # Foreign key to a content type, allowing a generic relation
    content_type = models.ForeignKey(
            ContentType,
            limit_choices_to=limit_choices,
            on_delete=models.CASCADE
            )
    # ID of the object to which this image belongs
    object_id = models.UUIDField()
    # This generic foreign key allows us to link to any model
    content_object = GenericForeignKey('content_type', 'object_id')

    # The user who created this
    owner = models.ForeignKey(User)
    # A caption for the image
    caption = models.TextField(blank=True)
    # The actual 'image' field stores stuff from Cloudinary
    image = CloudinaryField('image')
    # When the image was added
    creation_date = models.DateTimeField(auto_now_add=True)
    # Images can be assigned as the 'header image' of their site,
    # but only by the site's owner
    is_header_image = models.BooleanField(default=False)


class UserProfileImage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    image = CloudinaryField('image')
    user = models.OneToOneField(User, related_name='profile_image')
    creation_date = models.DateTimeField(auto_now_add=True)
