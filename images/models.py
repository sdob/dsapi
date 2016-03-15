import uuid
from actstream import action
from cloudinary.models import CloudinaryField
from django.db import models
from django.db.models import Q
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from divesites.models import Compressor, Divesite, Slipway


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

    def get_content_type_model(self):
        return self.content_type.model

    def save(self, *args, **kwargs):
        if self.is_header_image:
            # First we need to check whether there is an existing header
            # image for this image's content object
            try:
                # If we find something, then unset its is_header_image
                # flag and save before proceeding
                old_header_image = self.content_object.images.get(is_header_image=True)
                if old_header_image != self:
                    old_header_image.is_header_image = False
                    old_header_image.save()
            except Image.DoesNotExist:
                # If we find nothing, then we're OK
                pass
        # Either way, call our superclass method to actually
        # perform the save
        super(Image, self).save(*args, **kwargs)



class UserProfileImage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    image = CloudinaryField('image')
    user = models.OneToOneField(User, related_name='profile_image')
    creation_date = models.DateTimeField(auto_now_add=True)


def send_image_creation_action(sender, instance, created, **kwargs):
    if created:
        verb = 'added an image'
        action.send(instance.owner, verb=verb, action_object=instance, target=instance.content_object)
post_save.connect(send_image_creation_action, sender=Image)
