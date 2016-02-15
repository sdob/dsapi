from actstream.models import Action
from django.core.urlresolvers import reverse
from faker import Factory
from divesites.factories import DivesiteFactory, UserFactory
from rest_framework import status
from rest_framework.test import APITestCase

faker = Factory.create()

class ProfileFeedTestCase(APITestCase):

    def setUp(self):
        self.ds = DivesiteFactory()
        self.u = UserFactory()

    def test_can_retrieve_comment_activity(self):
        self.client.force_authenticate(self.u)
        response = self.client.post(reverse('divesitecomment-list'), {
            'text': faker.text(),
            'divesite': self.ds.id
            })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.client.get(reverse('profile-feed'))
        data = response.data
        self.assertEqual(len(data), 1)
        # We should never expose internal information
        #print(data[0].keys())
        #self.assertNotIn('actor_object_id', data[0].keys())

    def test_can_retrieve_dive_activity(self):
        self.client.force_authenticate(self.u)
        dt = faker.date_time_this_year()
        dt = faker.date_time_this_year()
        response = self.client.post(reverse('dive-list'), {
            'depth': faker.random_int(min=1, max=100),
            'duration': faker.random_int(min=1, max=100),
            'date': dt.date(),
            'time': dt.time(),
            'divesite': self.ds.id
            })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        a = Action.objects.all()[0]
        response = self.client.get(reverse('profile-feed'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
