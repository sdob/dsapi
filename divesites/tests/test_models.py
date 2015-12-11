from datetime import timedelta
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APITestCase

from divesites.models import Divesite
from divesites import factories

class DivesiteModelTestCase(APITestCase):

    def test_creation_succeeds(self):
        #ds = Divesite.objects.create()
        ds = factories.DivesiteFactory()
        ds.save()
        self.assertEqual(Divesite.objects.count(), 1)

    def test_max_latitude(self):
        try:
            ds = factories.DivesiteFactory(latitude=200)
            self.fail()
        except ValidationError:
            pass
    
    def test_min_latitude(self):
        try:
            ds = factories.DivesiteFactory(latitude=-90.01)
            self.fail()
        except ValidationError:
            pass

    def test_min_longitude(self):
        try:
            ds = factories.DivesiteFactory(longitude=-181)
            self.fail()
        except ValidationError:
            pass

    def test_max_longitude(self):
        try:
            ds = factories.DivesiteFactory(longitude=181)
            self.fail()
        except ValidationError:
            pass


class DiveModelTestCase(APITestCase):

    def test_foreign_key_is_set_correctly(self):
        d = factories.DiveFactory()
        self.assertTrue(Divesite.objects.filter(id=d.divesite.id).exists())
        pass

    def test_start_time_in_the_future(self):
        try:
            d = factories.DiveFactory(start_time=timezone.now()+timedelta(seconds=1))
            self.fail()
        except ValidationError:
            pass

    def test_diver_would_still_be_underwater(self):
        try:
            start_time = timezone.now() + timedelta(minutes=-30)
            duration = timedelta(minutes=60)
            d = factories.DiveFactory(start_time=start_time, duration=duration)
            self.fail()
        except ValidationError:
            pass

    def test_negative_duration(self):
        try:
            duration = timedelta(seconds=-60)
            d = factories.DiveFactory(duration=duration)
            self.fail('Negative duration %s should raise a ValidationError' % duration)
        except ValidationError:
            pass
