import os
from unittest.mock import patch

from django.contrib.contenttypes.models import ContentType
from django.core.files import File
from django.core.urlresolvers import reverse
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase
from divesites.models import Compressor, Divesite, Slipway
from divesites.factories import CompressorFactory, DivesiteFactory, SlipwayFactory, UserFactory
from dsapi import settings

from images.models import Image

COMPRESSOR_CTID = ContentType.objects.get_for_model(Compressor).id
DIVESITE_CTID = ContentType.objects.get_for_model(Divesite).id
SLIPWAY_CTID = ContentType.objects.get_for_model(Slipway).id

# Create your tests here.
class SanityCheckTestCase(APITestCase):

    def setUp(self):
        self.divesite = DivesiteFactory()
        self.owner = self.divesite.owner

    def test_nothing_explodes(self):
        i = Image(content_object=self.divesite, owner=self.owner)
        i.save()
        # Associated item is set correctly
        self.assertEqual(i.content_object, self.divesite)
        # Divesite knows about this image
        self.assertIn(i, self.divesite.images.all())

    def test_there_can_be_only_one(self):
        pass


@patch('cloudinary.uploader.call_api')
class ImageRetrievalTestCase(APITestCase):

    def setUp(self):
        self.image = File(open(os.path.join(settings.BASE_DIR, 'test.jpg'), 'rb'))
        self.owner = UserFactory()
        self.divesite = DivesiteFactory(owner=self.owner)
        self.compressor = CompressorFactory(owner=self.owner)
        self.slipway = SlipwayFactory(owner=self.owner)

    def test_can_retrieve_images(self, mock):
        i = Image(content_object=self.divesite, owner=self.owner)
        i.save()
        response = self.client.get(reverse('divesite-image-list', args=[self.divesite.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_can_post_images(self, mock):
        u2 = UserFactory()
        self.client.force_authenticate(u2)
        response = self.client.post(reverse('divesite-image-list', args=[self.divesite.id]), {
            'content_type': DIVESITE_CTID,
            'object_id': self.divesite.id,
            'image': self.image
            })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


@patch('cloudinary.uploader.call_api')
class HeaderImageRetrievalCase(APITestCase):

    def setUp(self):
        self.image = File(open(os.path.join(settings.BASE_DIR, 'test.jpg'), 'rb'))
        self.owner = UserFactory()
        self.compressor = CompressorFactory(owner=self.owner)
        self.divesite = DivesiteFactory(owner=self.owner)
        self.slipway = SlipwayFactory(owner=self.owner)

    def test_can_retrieve_divesite_image(self, mock):
        pass

    def test_returns_204_when_no_image(self, mock):
        pass


@patch('cloudinary.uploader.call_api')
class ImageCreateTestCase(APITestCase):

    def setUp(self):
        self.image = File(open(os.path.join(settings.BASE_DIR, 'test.jpg'), 'rb'))
        self.owner = UserFactory()
        self.compressor = CompressorFactory(owner=self.owner)
        self.divesite = DivesiteFactory(owner=self.owner)
        self.slipway = SlipwayFactory(owner=self.owner)

    def test_site_owner_can_set_header_image(self, mock):
        self.client.force_authenticate(self.owner)
        pass

    def test_only_site_owner_can_set_header_image(self, mock):
        pass

    def test_only_site_owner_can_set_header_image_in_update(self, mock):
        pass
