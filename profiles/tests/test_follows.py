from divesites.factories import DivesiteFactory, DiveFactory, UserFactory
from django.core.urlresolvers import reverse, NoReverseMatch
from faker import Factory as FakeFactory
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from profiles.models import Profile

faker = FakeFactory.create()

class FollowTestCase(APITestCase):

  def setUp(self):
    self.p1 = UserFactory().profile
    self.p2 = UserFactory().profile

  def test_following_someone_makes_them_a_follow_target(self):
    self.p1.follow_targets.add(self.p2)
    self.p1.save()
    self.assertTrue(self.p2 in self.p1.follow_targets.all())

  def test_following_is_asymmetrical(self):
    self.p1.follow_targets.add(self.p2)
    self.p1.save()
    self.assertFalse(self.p1 in self.p2.follow_targets.all())

