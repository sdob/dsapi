from actstream.actions import follow, unfollow
from actstream.models import Action, following, followers, user_stream
from django.core.urlresolvers import reverse
from faker import Factory
from divesites.factories import CompressorFactory, DivesiteFactory, SlipwayFactory, UserFactory
from rest_framework import status
from rest_framework.test import APITestCase

faker = Factory.create()

class ProfileFollowTestCase(APITestCase):

    def setUp(self):
        self.profile_to_follow = UserFactory().profile
        self.p = self.profile_to_follow

    def test_users_can_follow_other_users_on_the_model_side(self):
        u = UserFactory()
        self.client.force_authenticate(u)
        follow(u, self.profile_to_follow.user)
        self.assertEqual(len(following(u)), 1)
        self.assertEqual(len(followers(self.profile_to_follow.user)), 1)

    def test_users_can_see_other_users_activity_in_their_feeds_on_the_model_side(self):
        u = UserFactory()
        follow(u, self.profile_to_follow.user)
        ds = DivesiteFactory(owner=self.profile_to_follow.user)
        self.assertEqual(len(user_stream(u)), 1)
        a = user_stream(u)[0]
        self.assertEqual(a.actor_object_id, str(self.profile_to_follow.user.id))

    def test_users_can_see_who_they_are_following(self):
        u = UserFactory()
        follow(u, self.profile_to_follow.user)
        self.client.force_authenticate(u)
        response = self.client.get(reverse('profile-my-follows'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        data = response.data
        self.assertEqual(data[0]['id'], str(self.profile_to_follow.id))

    def test_users_can_follow_other_users(self):
        u = UserFactory()
        self.client.force_authenticate(u)
        url = reverse('profile-follow', args=[self.p.id])
        response = self.client.post(reverse('profile-follow', args=[self.p.id]), {})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Confirm that the user is now following
        response = self.client.get(reverse('profile-my-follows'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Have the followed user do something
        ds = DivesiteFactory(owner=self.p.user)
        # Confirm that the followed user's recent activity is in there
        response = self.client.get(reverse('profile-my-feed'))


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
        response = self.client.get(reverse('profile-my-feed'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data
        self.assertEqual(data['count'], 1)

    def test_can_retrieve_divesitecomment_activity(self):
        self.client.force_authenticate(self.u)
        response = self.client.post(reverse('divesitecomment-list'), {
            'text': faker.text(),
            'divesite': self.ds.id
            })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.client.get(reverse('profile-my-feed'))
        data = response.data
        self.assertEqual(data['count'], 1)

    def test_can_retrieve_slipwaycomment_activity(self):
        slipway = SlipwayFactory()
        self.client.force_authenticate(self.u)
        response = self.client.post(reverse('slipwaycomment-list'), {
            'text': faker.text(),
            'slipway': slipway.id,
            })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.client.get(reverse('profile-my-feed'))
        data = response.data
        self.assertEqual(data['count'], 1)

    def test_can_retrieve_compressorcomment_activity(self):
        compressor = CompressorFactory()
        self.client.force_authenticate(self.u)
        response = self.client.post(reverse('compressorcomment-list'), {
            'text': faker.text(),
            'compressor': compressor.id,
            })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.client.get(reverse('profile-my-feed'))
        data = response.data
        self.assertEqual(data['count'], 1)

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
        response = self.client.get(reverse('profile-my-feed'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data
        self.assertEqual(data['count'], 4)
