import os
from unittest.mock import patch

from django.core.files import File
from django.core.urlresolvers import reverse
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase
from divesites.models import Compressor, Divesite, Slipway
from divesites.factories import CompressorFactory, DivesiteFactory, SlipwayFactory, UserFactory
from dsapi import settings

from images.models import Image

# Create your tests here.
class SanityCheckTestCase(APITestCase):

    def setUp(self):
        self.divesite = DivesiteFactory()
        self.user = self.divesite.owner

    def test_nothing_explodes(self):
        i = Image(content_object=self.divesite, owner=self.user)
        i.save()
        # Associated item is set correctly
        self.assertEqual(i.content_object, self.divesite)
        # Divesite knows about this image
        self.assertIn(i, self.divesite.images.all())

    def test_there_can_be_only_one(self):
        pass

class ImageRetrievalTestCase(APITestCase):

    def setUp(self):
        self.divesite = DivesiteFactory()
        self.compressor = CompressorFactory()
        self.slipway = SlipwayFactory()

    def test_can_retrieve_images(self):
        i = Image(content_object=self.divesite, owner=self.user)
        i.save()


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
