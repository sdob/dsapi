from actstream.models import Action
from datetime import timedelta
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APITestCase

from divesites.models import Compressor, Dive, Divesite, Slipway
from divesites import factories

class CompressorModelTestCase(APITestCase):

    def test_creation_succeeds(self):
        c = factories.CompressorFactory()
        c.save()
        self.assertEqual(Compressor.objects.count(), 1)
        self.assertTrue(Action.objects.filter(target_object_id=c.id).exists())


class DivesiteModelTestCase(APITestCase):

    def test_creation_succeeds(self):
        ds = factories.DivesiteFactory()
        ds.save()
        self.assertEqual(Divesite.objects.count(), 1)
        self.assertTrue(Action.objects.filter(target_object_id=ds.id).exists())

    def test_max_latitude(self):
        with self.assertRaises(ValidationError):
            ds = factories.DivesiteFactory(latitude=200)
    
    def test_min_latitude(self):
        with self.assertRaises(ValidationError):
            ds = factories.DivesiteFactory(latitude=-90.01)

    def test_min_longitude(self):
        with self.assertRaises(ValidationError):
            ds = factories.DivesiteFactory(longitude=-181)

    def test_max_longitude(self):
        with self.assertRaises(ValidationError):
            ds = factories.DivesiteFactory(longitude=181)

    def test_get_average_maximum_depth_returns_expected_result(self):
        ds = factories.DivesiteFactory()
        for _ in range(10):
            factories.DiveFactory(depth=1, divesite=ds)
        self.assertEquals(ds.get_average_maximum_depth(), 1)

    def test_get_average_duration_returns_expected_result(self):
        ds = factories.DivesiteFactory()
        for _ in range(10):
            factories.DiveFactory(divesite=ds, duration=timedelta(seconds=120))
        self.assertEquals(Divesite.objects.get(id=ds.id).get_average_duration(), 2.0)
        self.assertEquals(factories.DivesiteFactory().get_average_duration(), 0)


class DiveModelTestCase(APITestCase):

    def test_creation_adds_an_action(self):
        user = factories.UserFactory()
        divesite = factories.DivesiteFactory()
        d = factories.DiveFactory(diver=user, divesite=divesite)
        self.assertTrue(Action.objects.filter(action_object_object_id=d.id).exists())
        self.assertEqual(Action.objects.filter(action_object_object_id=d.id).count(), 1)
        a = Action.objects.filter(action_object_object_id=d.id)[0]
        self.assertEqual(a.target_object_id, str(divesite.id))
        self.assertEqual(a.actor_object_id, str(user.id))

    def test_foreign_key_is_set_correctly(self):
        d = factories.DiveFactory()
        self.assertTrue(Divesite.objects.filter(id=d.divesite.id).exists())
