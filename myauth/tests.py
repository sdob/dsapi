import unittest
from django.core.urlresolvers import reverse
from django.test import TestCase
from .factories import UserFactory
from .models import User
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase
from rest_framework import status

# Create your tests here.
class UserTestCase(TestCase):

    def test_email_is_required(self):
        with self.assertRaises(ValueError):
            User.objects.create_user(email=None)

    def test_token_is_generated(self):
        user = UserFactory()
        self.assertTrue(Token.objects.filter(user=user).exists())
        self.assertEqual(Token.objects.filter(user=user).count(), 1)


class CreateUserViewTestCase(APITestCase):

    def test_sending_a_valid_email_and_password_works(self):
        email = 'valid.email@example.com'
        password = 'password'
        data = {'email': email, 'password': password}
        response = self.client.post(reverse('auth-create-user'), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_registering_duplicate_email_fails(self):
        email = 'valid.email@example.com'
        password = 'password'
        user = UserFactory(email=email)
        data = {'email': email, 'password': password}
        response = self.client.post(reverse('auth-create-user'), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # TODO: this should raise an exception somewhere, but I'll deal
    # with it later
    @unittest.skip('TODO...')
    def test_password_is_required(self):
        email = 'valid.email@example.com'
        data = {'email': email}
        response = self.client.post(reverse('auth-create-user'), data)


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
