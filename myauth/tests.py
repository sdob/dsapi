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
