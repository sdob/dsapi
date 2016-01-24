from datetime import timedelta
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APITestCase

from divesites.models import Divesite
from divesites import factories

class DivesiteModelTestCase(APITestCase):

    def test_creation_succeeds(self):
        ds = factories.DivesiteFactory()
        ds.save()
        self.assertEqual(Divesite.objects.count(), 1)

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

    def test_foreign_key_is_set_correctly(self):
        d = factories.DiveFactory()
        self.assertTrue(Divesite.objects.filter(id=d.divesite.id).exists())

    def test_start_time_in_the_future(self):
        with self.assertRaises(ValidationError):
            d = factories.DiveFactory(start_time=timezone.now()+timedelta(seconds=1))

    def test_diver_would_still_be_underwater(self):
        with self.assertRaises(ValidationError):
            start_time = timezone.now() + timedelta(minutes=-30)
            duration = timedelta(minutes=60)
            d = factories.DiveFactory(start_time=start_time, duration=duration)

    def test_negative_duration(self):
        with self.assertRaises(ValidationError):
            duration = timedelta(seconds=-60)
            d = factories.DiveFactory(duration=duration)
