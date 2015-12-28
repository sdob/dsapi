from django.test import TestCase
from .models import User

# Create your tests here.
class UserTestCase(TestCase):

    def test_email_is_required(self):
        with self.assertRaises(ValueError):
            User.objects.create_user(email=None)
