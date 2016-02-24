import uuid
from cloudinary.models import CloudinaryField
from django.db import models
from django.contrib.auth.models import User
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


# Create your models here.
class CompressorImage(BaseImage):
    compressor = models.ForeignKey(Compressor)

    def save(self, *args, **kwargs):
        if self.is_header_image:
            try:
                old_header = CompressorImage.objects.get(is_header_image=True)
                old_header.is_header_image = False
                old_header.save()
            except CompressorImage.DoesNotExist:
                pass
        super(CompressorImage, self).save(*args, **kwargs)


class DivesiteImage(BaseImage):
    divesite = models.ForeignKey(Divesite)

    def save(self, *args, **kwargs):
        if self.is_header_image:
            try:
                old_header = DivesiteImage.objects.get(is_header_image=True)
                old_header.is_header_image = False
                old_header.save()
            except DivesiteImage.DoesNotExist:
                pass
        super(DivesiteImage, self).save(*args, **kwargs)


class SlipwayImage(BaseImage):
    slipway = models.ForeignKey(Slipway)

    def save(self, *args, **kwargs):
        if self.is_header_image:
            try:
                old_header = SlipwayImage.objects.get(is_header_image=True)
                old_header.is_header_image = False
                old_header.save()
            except SlipwayImage.DoesNotExist:
                pass
        super(SlipwayImage, self).save(*args, **kwargs)


class UserProfileImage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    image = CloudinaryField('image')
    user = models.OneToOneField(User, related_name='profile_image')
    creation_date = models.DateTimeField(auto_now_add=True)
