from actstream.models import Action
from django.core.urlresolvers import reverse
from faker import Factory
from divesites.factories import CompressorFactory, DivesiteFactory, SlipwayFactory, UserFactory
from rest_framework import status
from rest_framework.test import APITestCase

faker = Factory.create()

class ProfileFeedTestCase(APITestCase):

    def setUp(self):
        self.ds = DivesiteFactory()
        self.u = UserFactory()

    def test_can_retrieve_dive_activity(self):
        self.client.force_authenticate(self.u)
        dt = faker.date_time_this_year()
        response = self.client.post(reverse('dive-list'), {
            'depth': faker.random_int(min=1, max=100),
            'duration': faker.random_int(min=1, max=100),
            'date': dt.date(),
            'time': dt.time(),
            'divesite': self.ds.id
            })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.client.get(reverse('profile-feed'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_can_retrieve_divesitecomment_activity(self):
        self.client.force_authenticate(self.u)
        response = self.client.post(reverse('divesitecomment-list'), {
            'text': faker.text(),
            'divesite': self.ds.id
            })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.client.get(reverse('profile-feed'))
        data = response.data
        self.assertEqual(len(data), 1)

    def test_can_retrieve_slipwaycomment_activity(self):
        slipway = SlipwayFactory()
        self.client.force_authenticate(self.u)
        response = self.client.post(reverse('slipwaycomment-list'), {
            'text': faker.text(),
            'slipway': slipway.id,
            })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.client.get(reverse('profile-feed'))
        data = response.data
        self.assertEqual(len(data), 1)

    def test_can_retrieve_compressorcomment_activity(self):
        compressor = CompressorFactory()
        self.client.force_authenticate(self.u)
        response = self.client.post(reverse('compressorcomment-list'), {
            'text': faker.text(),
            'compressor': compressor.id,
            })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.client.get(reverse('profile-feed'))
        data = response.data
        self.assertEqual(len(data), 1)

    def test_can_retrieve_activity_for_mixed_types(self):
        slipway = SlipwayFactory()
        compressor = CompressorFactory()
        self.client.force_authenticate(self.u)

        # Add a slipway comment
        response = self.client.post(reverse('slipwaycomment-list'), {
            'text': faker.text(),
            'slipway': slipway.id,
            })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Add a compressor comment
        response = self.client.post(reverse('compressorcomment-list'), {
            'text': faker.text(),
            'compressor': compressor.id,
            })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Add a divesite comment
        response = self.client.post(reverse('divesitecomment-list'), {
            'text': faker.text(),
            'divesite': self.ds.id
            })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Log a dive
        dt = faker.date_time_this_year()
        response = self.client.post(reverse('dive-list'), {
            'depth': faker.random_int(min=1, max=100),
            'duration': faker.random_int(min=1, max=100),
            'date': dt.date(),
            'time': dt.time(),
            'divesite': self.ds.id
            })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Get our feed
        response = self.client.get(reverse('profile-feed'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 4)
