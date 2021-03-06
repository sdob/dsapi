from actstream.models import Action, user_stream
from faker import Factory
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase
from divesites.factories import DivesiteFactory, UserFactory
from comments.factories import DivesiteCommentFactory
from comments.models import DivesiteComment

faker = Factory.create()

# Create your tests here.
class SanityCheckTestCase(APITestCase):

    def setUp(self):
        self.ds = DivesiteFactory()
        pass

    def test_divesite_comments_are_retrievable(self):
        c = DivesiteCommentFactory(divesite=self.ds)
        response = self.client.get(reverse('divesite-comments', args=[self.ds.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_divesite_comments_can_be_added(self):
        u = UserFactory()
        self.client.force_authenticate(u)
        text = faker.text()
        data = {
                'text': text,
                'divesite': self.ds.id
                }
        response = self.client.post(reverse('divesitecomment-list'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_divesite_comments_can_be_removed(self):
        u = UserFactory()
        c = DivesiteCommentFactory(divesite=self.ds, owner=u)
        self.client.force_authenticate(u)
        response = self.client.delete(reverse('divesitecomment-detail', args=[c.id]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_divesite_comments_can_be_edited(self):
        u = UserFactory()
        c = DivesiteCommentFactory(divesite=self.ds, owner=u)
        self.client.force_authenticate(u)
        old_text = c.text
        new_text = faker.text()
        data = {'text': new_text}
        response = self.client.patch(reverse('divesitecomment-detail', args=[c.id]), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_only_owner_can_edit(self):
        u = UserFactory()
        c = DivesiteCommentFactory(divesite=self.ds)
        self.client.force_authenticate(u)
        old_text = c.text
        new_text = faker.text()
        data = {'text': new_text}
        response = self.client.patch(reverse('divesitecomment-detail', args=[c.id]), data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class ActivityCreationTestCase(APITestCase):
    
    def setUp(self):
        self.u  = UserFactory()
        self.ds = DivesiteFactory()

    def test_commenting_creates_an_action(self):
        self.client.force_authenticate(self.u)
        data = {
                'text': faker.text(),
                'divesite': self.ds.id
                }
        response = self.client.post(reverse('divesitecomment-list'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        stream = user_stream(self.u, with_user_activity=True)
        self.assertEqual(len(stream), 1)

    def test_created_action_has_a_target_and_an_action_object(self):
        self.client.force_authenticate(self.u)
        data = {
                'text': faker.text(),
                'divesite': self.ds.id
                }
        response = self.client.post(reverse('divesitecomment-list'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        comment = DivesiteComment.objects.get(divesite=self.ds)
        stream = user_stream(self.u, with_user_activity=True)
        a = stream[0]
        self.assertEqual(a.target, self.ds)
        self.assertEqual(a.action_object, comment)
