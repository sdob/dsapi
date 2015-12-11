from divesites.factories import DivesiteFactory, DiveFactory
from django.core.urlresolvers import reverse, NoReverseMatch
from faker import Factory as FakeFactory
from rest_framework import status
from rest_framework.test import APITestCase
from myauth.factories import UserFactory
from myauth.models import User
from profiles.models import Profile

faker = FakeFactory.create()

class ProfileSaveViewsTestCase(APITestCase):
    def test_happy_path(self):
        response = self.client.get(reverse('profile-detail', args=[self.p.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.p.id)

    def setUp(self):
        user = UserFactory()
        user.profile.name = faker.name()
        user.profile.save()
        self.p = user.profile

    def test_retrieve_users_dives(self):
        for _ in xrange(10):
            d = DiveFactory(diver=self.p.user)

        response = self.client.get(reverse('profile-dives', args=[self.p.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertEqual(len(response.data), 10)

    def test_retrieve_users_divesites(self):
        for _ in xrange(3):
            ds = DivesiteFactory(owner=self.p.user)

        response = self.client.get(reverse('profile-divesites', args=[self.p.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertEqual(len(response.data), 3)

    def test_listing_profiles_is_undefined(self):
        try:
            self.client.get(reverse('profile-list', args=[self.p.id]))
            fail('reversing "profile-list" should raise a NoReverseMatch exception')
        except NoReverseMatch:
            pass


class ProfileCreateTestCase(APITestCase):

    def setUp(self):
        user = UserFactory()
        user.profile.name = faker.name()
        user.profile.save()
        self.p = user.profile

    def test_creating_profiles_is_undefined(self):
        try:
            self.client.post(reverse('profile-list', args=[self.p.id]))
            fail('reversing "profile-list" should raise a NoReverseMatch exception')
        except NoReverseMatch:
            pass


class ProfileDeleteTestCase(APITestCase):

    def setUp(self):
        user = UserFactory()
        user.profile.name = faker.name()
        user.profile.save()
        self.p = user.profile

    def test_creating_profiles_is_undefined(self):
        try:
            self.client.delete(reverse('profile-list', args=[self.p.id]))
            fail('reversing "profile-list" should raise a NoReverseMatch exception')
        except NoReverseMatch:
            pass


class ProfileUpdateTestCase(APITestCase):

    def setUp(self):
        user = UserFactory()
        user.profile.name = faker.name()
        user.profile.save()
        self.p = user.profile

    def test_updating_profile_requires_authentication(self):
        data = {'name': 'Nosmo King'}
        response = self.client.patch(reverse('profile-detail', args=[self.p.id]), data=data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_an_authenticated_user_can_update_their_profile(self):
        new_name = 'Nosmo King'
        data = {'name': new_name}
        self.client.force_authenticate(self.p.user)
        response = self.client.patch(reverse('profile-detail', args=[self.p.id]), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Profile.objects.get(id=self.p.id).name, new_name)

    def test_an_authenticated_user_can_only_update_their_own_profile(self):
        new_name = 'Nosmo King'
        old_name = self.p.name
        data = {'name': new_name}
        user2 = UserFactory()
        self.client.force_authenticate(user2)
        response = self.client.patch(reverse('profile-detail', args=[self.p.id]), data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Profile.objects.get(id=self.p.id).name, old_name)
