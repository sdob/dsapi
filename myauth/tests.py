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
