import os
from unittest.mock import patch

from django.core.files import File
from django.core.urlresolvers import reverse, NoReverseMatch
from django.contrib.auth.models import User
from faker import Factory as FakeFactory
from rest_framework import status
from rest_framework.test import APITestCase

from dsapi import settings
from divesites.factories import DivesiteFactory, DiveFactory, UserFactory
from images.models import UserProfileImage
from profiles.models import Profile

faker = FakeFactory.create()

class OwnProfileViewTestCase(APITestCase):
    def setUp(self):
        user = UserFactory()
        user.profile.name = faker.name()
        user.profile.about_me = faker.text()
        user.profile.save()
        self.p = user.profile

    def test_returns_401_if_unauthorized(self):
        response = self.client.get(reverse('profile-me'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_returns_200_if_authorized(self):
        self.client.force_authenticate(self.p.user)
        response = self.client.get(reverse('profile-me'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_returns_expected_data(self):
        self.client.force_authenticate(self.p.user)
        response = self.client.get(reverse('profile-me'))
        u = self.p.user
        data = response.data
        self.assertEquals(data['name'], self.p.name)
        self.assertEquals(data['email'], self.p.user.email)
        self.assertEquals(data['about_me'], self.p.about_me)


class ProfileViewsTestCase(APITestCase):
    def test_happy_path(self):
        response = self.client.get(reverse('profile-detail', args=[self.p.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], str(self.p.id))

    def setUp(self):
        user = UserFactory()
        user.profile.name = faker.name()
        user.profile.save()
        self.p = user.profile

    def test_email_address_is_not_returned(self):
        response = self.client.get(reverse('profile-detail', args=[self.p.id]))
        self.assertFalse('email' in response.data.keys())

    def test_retrieve_users_dives(self):
        for _ in range(10):
            d = DiveFactory(diver=self.p.user)

        response = self.client.get(reverse('profile-dives', args=[self.p.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertEqual(len(response.data), 10)

    def test_retrieve_users_divesites(self):
        for _ in range(3):
            ds = DivesiteFactory(owner=self.p.user)

        response = self.client.get(reverse('profile-divesites', args=[self.p.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertEqual(len(response.data), 3)

    def test_listing_profiles_is_undefined(self):
        with self.assertRaises(NoReverseMatch):
            self.client.get(reverse('profile-list', args=[self.p.id]))


class ProfileCreateTestCase(APITestCase):

    def setUp(self):
        user = UserFactory()
        user.profile.name = faker.name()
        user.profile.save()
        self.p = user.profile

    def test_creating_profiles_is_undefined(self):
        with self.assertRaises(NoReverseMatch):
            self.client.post(reverse('profile-list', args=[self.p.id]))


class ProfileDeleteTestCase(APITestCase):

    def setUp(self):
        user = UserFactory()
        user.profile.name = faker.name()
        user.profile.save()
        self.p = user.profile

    def test_creating_profiles_is_undefined(self):
        with self.assertRaises(NoReverseMatch):
            self.client.delete(reverse('profile-list', args=[self.p.id]))


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


@patch('cloudinary.uploader.call_api')
class ProfileImageTestCase(APITestCase):

    def setUp(self):
        self.image = File(open(os.path.join(settings.BASE_DIR, 'test.jpg'), 'rb'))
        self.user = UserFactory()

    def test_post_image(self, mock):
        data = { 'image': self.image }
        # Try when unauthenticated
        response = self.client.post(reverse('profile-profile-image',
            args=[self.user.profile.id]), data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Try when authenticated as someone else
        self.client.force_authenticate(user=UserFactory())
        response = self.client.post(reverse('profile-profile-image',
            args=[self.user.profile.id]), data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Try when authenticated as the user
        self.client.force_authenticate(self.user)
        response = self.client.post(reverse('profile-profile-image',
            args=[self.user.profile.id]), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(UserProfileImage.objects.filter(user=self.user).count(), 1)

        # Check that we overwrite the image
        response = self.client.post(reverse('profile-profile-image',
            args=[self.user.profile.id]), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(UserProfileImage.objects.filter(user=self.user).count(), 1)

    def test_retrieve_image(self, mock):
        # Try when there's nothing to retrieve
        response = self.client.get(reverse('profile-profile-image', args=[self.user.profile.id]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.client.force_authenticate(self.user)
        data = { 'image': self.image }
        response = self.client.post(reverse('profile-profile-image',
            args=[self.user.profile.id]), data)
        response = self.client.get(reverse('profile-profile-image', args=[self.user.profile.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        print(response.data)


    def test_delete_route(self, mock):
        # Try when unauthenticated
        response = self.client.delete(reverse('profile-profile-image', args=[self.user.profile.id]))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Try when authenticated as someone else
        self.client.force_authenticate(user=UserFactory())
        response = self.client.delete(reverse('profile-profile-image', args=[self.user.profile.id]))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Try when authenticated as the user
        self.client.force_authenticate(self.user)
        response = self.client.delete(reverse('profile-profile-image', args=[self.user.profile.id]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
