import unittest
from django.core.urlresolvers import reverse
from django.test import TestCase
from .factories import UserFactory
from .models import User
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase
from rest_framework import status

class TokenAuthenticationTestCase(APITestCase):
    def test_sending_username_and_password_returns_token(self):
        password = 'ilovecheese'
        user = UserFactory(password=password)
        email = user.email
        url = reverse('auth-endpoint')
        result = self.client.post(url, {'username': email, 'password': password})
        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertIn('token', result.data.keys())
        self.assertEqual(result.data['token'], Token.objects.get(user=user).key)


class UserRegistrationTestCase(APITestCase):

    def test_registering_with_existing_email_fails(self):
        email = 'testuser@example.com'
        password = 'somevalidpass'
        u = UserFactory(email=email)
        data = {'email': email, 'password': password}
        response = self.client.post(reverse('auth-register'), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_registering_with_a_new_email_address_succeeds(self):
        email = 'testuser@example.com'
        password = 'somevalidpassword'
        data = {'email': email, 'password': password}
        response = self.client.post(reverse('auth-register'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email=email).exists())

    def test_full_name_is_added_to_profile(self):
        email = 'testuser@example.com'
        password = 'somevalidpassword'
        full_name = 'Joe Bloggs'
        data = {'email': email, 'password': password, 'full_name': full_name}
        response = self.client.post(reverse('auth-register'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.get(email=email).profile.name, full_name)
