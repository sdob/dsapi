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

from images.models import CompressorImage, DivesiteImage, SlipwayImage

# Create your tests here.
class SanityCheckTestCase(APITestCase):

    def setUp(self):
        self.divesite = DivesiteFactory()
        self.user = self.divesite.owner

    def test_nothing_explodes(self):
        i = DivesiteImage(divesite=self.divesite, owner=self.user)
        i.save()
        self.assertEqual(i.divesite, self.divesite)

    def test_there_can_be_only_one(self):
        i1 = DivesiteImage(divesite=self.divesite, owner=self.user, is_header_image=True)
        i1.save()
        self.assertTrue(i1.is_header_image)
        i2 = DivesiteImage(divesite=self.divesite, owner=self.user, is_header_image=True)
        i2.save()
        # Check that i1 is no longer a header image
        i1 = DivesiteImage.objects.get(id=i1.id)
        self.assertFalse(i1.is_header_image)
        # Check that i2 is now a header image
        i2 = DivesiteImage.objects.get(id=i2.id)
        self.assertTrue(i2.is_header_image)

class ImageRetrievalTestCase(APITestCase):

    def setUp(self):
        self.divesite = DivesiteFactory()
        self.compressor = CompressorFactory()
        self.slipway = SlipwayFactory()

    def test_can_retrieve_images(self):
        response = self.client.get(reverse('compressor-images', args=[self.compressor.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get(reverse('divesite-images', args=[self.divesite.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get(reverse('slipway-images', args=[self.slipway.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)


@patch('cloudinary.uploader.call_api')
class HeaderImageRetrievalCase(APITestCase):

    def setUp(self):
        self.image = File(open(os.path.join(settings.BASE_DIR, 'test.jpg'), 'rb'))
        self.owner = UserFactory()
        self.compressor = CompressorFactory(owner=self.owner)
        self.divesite = DivesiteFactory(owner=self.owner)
        self.slipway = SlipwayFactory(owner=self.owner)

    def test_can_retrieve_divesite_image(self, mock):
        self.client.force_authenticate(self.owner)

        # Divesites
        response = self.client.post(reverse('divesiteimage-list'), {
            'divesite': self.divesite.id,
            'image': self.image,
            'is_header_image': True
            })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.client.get(reverse('divesite-header', args=[self.divesite.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Compressors
        response = self.client.post(reverse('compressorimage-list'), {
            'compressor': self.compressor.id,
            'image': self.image,
            'is_header_image': True
            })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.client.get(reverse('compressor-header', args=[self.compressor.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Slipways
        response = self.client.post(reverse('slipwayimage-list'), {
            'slipway': self.slipway.id,
            'image': self.image,
            'is_header_image': True
            })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.client.get(reverse('slipway-header', args=[self.slipway.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_returns_204_when_no_image(self, mock):
        response = self.client.get(reverse('divesite-header', args=[self.divesite.id]))
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
        data = {
                'divesite': self.divesite.id,
                'image': self.image,
                'is_header_image': True
                }
        response = self.client.post(reverse('divesiteimage-list'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


    def test_only_site_owner_can_set_header_image(self, mock):
        u2 = UserFactory()
        data = {
                'divesite': self.divesite.id,
                'is_header_image': True
                }
        self.client.force_authenticate(u2)
        # Compressors
        response = self.client.post(reverse('compressorimage-list'), {
            'compressor': self.compressor.id,
            'image': self.image,
            'is_header_image': True
            })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        # Divesites
        response = self.client.post(reverse('divesiteimage-list'), {
            'divesite': self.divesite.id,
            'image': self.image,
            'is_header_image': True
            })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        # Slipways
        response = self.client.post(reverse('slipwayimage-list'), {
            'slipway': self.slipway.id,
            'image': self.image,
            'is_header_image': True
            })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_only_site_owner_can_set_header_image_in_update(self, mock):
        u2 = UserFactory()
        self.client.force_authenticate(u2)
        # Compressors
        response = self.client.post(reverse('compressorimage-list'), {
            'compressor': self.compressor.id,
            'image': self.image
            })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        compressor_id = response.data['id']
        response = self.client.patch(reverse('compressorimage-detail', args=[compressor_id]), {
            'compressor': self.compressor.id,
            'is_header_image': True
            })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Divesites
        response = self.client.post(reverse('divesiteimage-list'), {
            'divesite': self.divesite.id,
            'image': self.image
            })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        divesite_id = response.data['id']
        response = self.client.patch(reverse('divesiteimage-detail', args=[divesite_id]), {
            'divesite': self.divesite.id,
            'is_header_image': True
            })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Slipways
        response = self.client.post(reverse('slipwayimage-list'), {
            'slipway': self.slipway.id,
            'image': self.image
            })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        slipway_id = response.data['id']
        response = self.client.patch(reverse('slipwayimage-detail', args=[slipway_id]), {
            'slipway': self.slipway.id,
            'is_header_image': True
            })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
