from django.test import TestCase
from rest_framework.test import APITestCase
from divesites.factories import DiveFactory, DivesiteFactory
from activity.models import Activity, DiveLog, DivesiteCreation
from activity.serializers import serializer_factory
from myauth.factories import UserFactory

# Create your tests here.

class ActivitySignalTestCase(APITestCase):

    def setUp(self):
        pass

    def test_logging_dive_creates_activity_record(self):
        d = DiveFactory()
        self.assertTrue(DiveLog.objects.filter(dive=d).exists())
        dl = DiveLog.objects.get(dive=d)
        self.assertEqual(dl.user, d.diver)

    def test_creating_divesite_creates_activity_record(self):
        ds = DivesiteFactory()
        self.assertTrue(DivesiteCreation.objects.filter(divesite=ds).exists())
        dc = DivesiteCreation.objects.get(divesite=ds)
        self.assertEqual(dc.user, ds.owner)

    def test_i_can_get_various_activities(self):
        ds = DivesiteFactory()
        d = DiveFactory(divesite=ds)
        self.assertEqual(Activity.objects.count(), 2)
        try:
            creation = DivesiteCreation.objects.get(divesite=ds)
            self.assertEqual(creation.divesite, ds)
        except DivesiteCreation.DoesNotExist:
            log_entry = DiveLog.objects.get(dive=d)
            self.assertEqual(log_entry.dive, d)


class ActivitySerializationTestCase(APITestCase):

    def setUp(self):
        self.u = UserFactory()
        self.ds = DivesiteFactory(owner=self.u)
        self.d = DiveFactory(divesite=self.ds, diver=self.u)

    def test_correct_fields(self):
        for a in Activity.objects.all().select_subclasses():
            s = serializer_factory(a)(a)
            data = s.data
            self.assertIn('user', data.keys())
            self.assertIn('id', data['user'].keys())
            self.assertEqual(data['user']['id'], self.u.profile.id)
            self.assertIn('name', data['user'].keys())
            self.assertEqual(data['user']['name'], self.u.profile.name)
            self.assertIn('creation_date', data.keys())

            self.assertTrue('dive' in data.keys() or 'divesite' in data.keys())
            if 'dive' in data.keys():
                pass
                # TODO: check dive fields
            else:
                pass
                # TODO: check divesite fields
