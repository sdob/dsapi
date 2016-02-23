from django.test import TestCase
from rest_framework.test import APITestCase
from divesites.models import Compressor, Divesite, Slipway
from divesites.factories import CompressorFactory, DivesiteFactory, SlipwayFactory

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
