from actstream.models import user_stream
from django.core.urlresolvers import reverse
from faker import Factory
from rest_framework import status
from rest_framework.test import APITestCase
from divesites.factories import DiveFactory, DivesiteFactory, UserFactory

faker = Factory.create()

class DiveLogActionCreationTestCase(APITestCase):

    def setUp(self):
        self.u = UserFactory()
        self.ds = DivesiteFactory()

    def test_logging_a_dive_creates_an_action(self):
        self.client.force_authenticate(self.u)
        dt = faker.date_time_this_year()
        data = {
                'depth': faker.random_int(min=1, max=100),
                'duration': faker.random_int(min=1, max=100),
                'date': dt.date(),
                'time': dt.time(),
                'divesite': self.ds.id
                }
        result = self.client.post(reverse('dive-list'), data)
        self.assertEqual(result.status_code, status.HTTP_201_CREATED)
        stream = user_stream(self.u, with_user_activity=True)
        self.assertEqual(len(stream), 1)
