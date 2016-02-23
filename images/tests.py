from django.core.urlresolvers import reverse
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase
from divesites.models import Compressor, Divesite, Slipway
from divesites.factories import CompressorFactory, DivesiteFactory, SlipwayFactory, UserFactory

from images.models import CompressorImage, DivesiteImage, SlipwayImage

# Create your tests here.
class SanityCheckTestCase(APITestCase):

    def setUp(self):
        self.ds = DivesiteFactory()
        self.user = self.ds.owner

    def test_nothing_explodes(self):
        i = DivesiteImage(divesite=self.ds, owner=self.user)
        i.save()
        self.assertEqual(i.divesite, self.ds)

    def test_there_can_be_only_one(self):
        i1 = DivesiteImage(divesite=self.ds, owner=self.user, is_header_image=True)
        i1.save()
        self.assertTrue(i1.is_header_image)
        i2 = DivesiteImage(divesite=self.ds, owner=self.user, is_header_image=True)
        i2.save()
        # Check that i1 is no longer a header image
        i1 = DivesiteImage.objects.get(id=i1.id)
        self.assertFalse(i1.is_header_image)
        # Check that i2 is now a header image
        i2 = DivesiteImage.objects.get(id=i2.id)
        self.assertTrue(i2.is_header_image)


class ImageCreateTestCase(APITestCase):

    def setUp(self):
        self.owner = UserFactory()
        self.compressor = CompressorFactory(owner=self.owner)
        self.ds = DivesiteFactory(owner=self.owner)
        self.slipway = SlipwayFactory(owner=self.owner)

    def test_site_owner_can_set_header_image(self):
        self.client.force_authenticate(self.owner)
        data = {
                'divesite': self.ds.id,
                'is_header_image': True
                }
        response = self.client.post(reverse('divesiteimage-list'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_only_site_owner_can_set_header_image(self):
        u2 = UserFactory()
        data = {
                'divesite': self.ds.id,
                'is_header_image': True
                }
        self.client.force_authenticate(u2)
        response = self.client.post(reverse('divesiteimage-list'), data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        response = self.client.post(reverse('compressorimage-list'), {
            'compressor': self.compressor.id,
            'is_header_image': True
            })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        response = self.client.post(reverse('slipwayimage-list'), {
            'slipway': self.slipway.id,
            'is_header_image': True
            })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_only_site_owner_can_set_header_image_in_update(self):
        u2 = UserFactory()
        data = {

                }
