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

    def test_there_can_be_only_one_header_image(self):
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
        response = self.client.post(reverse('compressor-image-list', args=[self.compressor.id]), {
            'content_type': COMPRESSOR_CTID,
            'object_id': self.compressor.id,
            'image': self.image
            })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.client.post(reverse('divesite-image-list', args=[self.divesite.id]), {
            'content_type': DIVESITE_CTID,
            'object_id': self.divesite.id,
            'image': self.image
            })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.client.post(reverse('slipway-image-list', args=[self.slipway.id]), {
            'content_type': SLIPWAY_CTID,
            'object_id': self.slipway.id,
            'image': self.image
            })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_can_retrieve_user_images(self, mock):
        response = self.client.get(reverse('profile-images', args=[self.owner.profile.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertEqual(len(response.data), 0)
        num_images = 5
        for _ in range(num_images):
            i = Image(content_object=self.divesite, owner=self.owner)
            i.save()
        response = self.client.get(reverse('profile-images', args=[self.owner.profile.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertEqual(len(response.data), num_images)

    def test_can_delete_own_images(self, mock):
        u2 = UserFactory()
        self.client.force_authenticate(u2)
        response = self.client.post(reverse('compressor-image-list', args=[self.compressor.id]), {
            'content_type': COMPRESSOR_CTID,
            'object_id': self.compressor.id,
            'image': self.image
            })
        image_id = response.data['id']
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.client.delete(reverse('compressor-image-detail', args=[self.compressor.id, image_id]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_cant_delete_others_images(self, mock):
        u2 = UserFactory()
        self.client.force_authenticate(u2)
        response = self.client.post(reverse('compressor-image-list', args=[self.compressor.id]), {
            'content_type': COMPRESSOR_CTID,
            'object_id': self.compressor.id,
            'image': self.image
            })
        image_id = response.data['id']
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.client.logout()
        self.client.force_authenticate(self.owner)
        response = self.client.delete(reverse('compressor-image-detail', args=[self.compressor.id, image_id]))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


@patch('cloudinary.uploader.call_api')
class HeaderImageRetrievalCase(APITestCase):

    def setUp(self):
        self.image = File(open(os.path.join(settings.BASE_DIR, 'test.jpg'), 'rb'))
        self.owner = UserFactory()
        self.compressor = CompressorFactory(owner=self.owner)
        self.divesite = DivesiteFactory(owner=self.owner)
        self.slipway = SlipwayFactory(owner=self.owner)

    def test_can_retrieve_site_header_image(self, mock):
        self.client.force_authenticate(self.owner)
        response = self.client.post(reverse('divesite-header-image', args=[self.divesite.id]), {
            'image': self.image
            })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.client.get(reverse('divesite-header-image', args=[self.divesite.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_returns_204_when_no_image(self, mock):
        response = self.client.get(reverse('divesite-header-image', args=[self.divesite.id]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


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
