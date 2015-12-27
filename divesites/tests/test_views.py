from django.utils import timezone
from datetime import timedelta
import random
from django.utils import timezone
from django.core.urlresolvers import reverse
import factory
from faker import Factory as FakerFactory
from rest_framework import status
from rest_framework.test import APITestCase
from divesites import factories
from divesites.models import Dive, Divesite
from divesites.factories import DiveFactory, DivesiteFactory
from myauth.factories import UserFactory
from profiles.models import Profile

NUM_SITES = 4
NUM_DIVES = 10

faker = FakerFactory.create()

class DivesiteSafeViewsTestCase(APITestCase):

    def setUp(self):
        for _ in xrange(NUM_SITES):
            ds = factories.DivesiteFactory()

    def test_list_view_returns_200(self):
        result = self.client.get(reverse('divesite-list'))
        self.assertEqual(result.status_code, status.HTTP_200_OK)

    def test_list_view_returns_list(self):
        result = self.client.get(reverse('divesite-list'))
        self.assertIsInstance(result.data, list)
        self.assertEqual(len(result.data), NUM_SITES)

    def test_detail_view_returns_200(self):
        ds = Divesite.objects.all()[0]
        result = self.client.get(reverse('divesite-detail', args=[ds.id]))
        self.assertEqual(result.status_code, status.HTTP_200_OK)

    def test_detail_view_returns_expected_fields(self):
        ds = Divesite.objects.all()[0]
        data = self.client.get(reverse('divesite-detail', args=[ds.id])).data
        self.assertEqual(data['name'], ds.name)
        self.assertEqual(data['id'], str(ds.id))
        self.assertEqual(data['owner']['id'], ds.owner.profile.id)


class DivesiteCreateTestCase(APITestCase):

    def setUp(self):
        self.u = UserFactory()
        latitude = faker.latitude()
        longitude = faker.longitude()
        name = "Test Divesite"
        level = 0
        self.data = {"latitude": latitude, "longitude": longitude, "name": name, "level": level}

    def test_unauthenticated_create_returns_401(self):
        result = self.client.post(reverse('divesite-list'), self.data)
        self.assertEqual(result.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthenticated_create_doesnt_create_a_divesite(self):
        count = Divesite.objects.count()
        result = self.client.post(reverse('divesite-list'), self.data)
        self.assertEqual(count, Divesite.objects.count())

    def test_authenticated_create_returns_201(self):
        self.client.force_authenticate(self.u)
        result = self.client.post(reverse('divesite-list'), self.data)
        self.assertEqual(result.status_code, status.HTTP_201_CREATED)

    def test_authenticated_create_adds_a_divesite(self):
        count = Divesite.objects.count()
        self.client.force_authenticate(self.u)
        result = self.client.post(reverse('divesite-list'), self.data)
        self.assertEqual(Divesite.objects.count(), count + 1)
        self.assertTrue(Divesite.objects.filter(name=self.data['name']).exists())


class DivesiteUpdateTestCase(APITestCase):

    def setUp(self):
        self.user = UserFactory()
        self.ds = DivesiteFactory(owner=self.user)

    def test_unauthenticated_update_returns_401(self):
        data = {'name': 'New Divesite Name'}
        result = self.client.patch(reverse('divesite-detail', args=[self.ds.id]), data)
        self.assertEqual(result.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_divesite_owner_can_update(self):
        data = {'name': 'New Divesite Name'}
        self.client.force_authenticate(user=self.user)
        result = self.client.patch(reverse('divesite-detail', args=[self.ds.id]), data)
        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertEqual(Divesite.objects.get(id=self.ds.id).name, 'New Divesite Name')

    def test_only_divesite_owner_can_update(self):
        data = {'name': 'New Divesite Name'}
        user2 = UserFactory()
        self.client.force_authenticate(user2)
        self.assertFalse(user2 == self.ds.owner)
        result = self.client.patch(reverse('divesite-detail', args=[self.ds.id]), data)
        self.assertEqual(result.status_code, status.HTTP_403_FORBIDDEN)

    def test_ownership_is_not_editable(self):
        old_name = self.ds.name
        new_name = 'New Divesite Name'
        user2 = UserFactory()
        data = {'owner': user2.profile}
        self.client.force_authenticate(self.user)
        result = self.client.patch(reverse('divesite-detail', args=[self.ds.id]), data)
        self.assertEqual(Divesite.objects.get(id=self.ds.id).name, old_name)


class DiveSafeViewsTestCase(APITestCase):

    def setUp(self):
        self.ds0, self.ds1 = factories.DivesiteFactory(), factories.DivesiteFactory()
        for _ in xrange(NUM_DIVES):
            d = factories.DiveFactory(divesite=self.ds0)

    def test_list_of_related_dives_returns_200(self):
        result = self.client.get(reverse('divesite-dives', args=[self.ds0.id]))
        self.assertEqual(result.status_code, status.HTTP_200_OK)

    def test_list_of_related_dives_returns_list(self):
        result = self.client.get(reverse('divesite-dives', args=[self.ds0.id]))
        self.assertIsInstance(result.data, list)
        self.assertEqual(len(result.data), NUM_DIVES)

    def test_list_of_related_dives_returns_200_if_empty(self):
        result = self.client.get(reverse('divesite-dives', args=[self.ds1.id]))
        self.assertEqual(result.status_code, status.HTTP_200_OK)

    def test_list_of_related_dives_returns_empty_list(self):
        result = self.client.get(reverse('divesite-dives', args=[self.ds1.id]))
        self.assertIsInstance(result.data, list)
        self.assertEqual(len(result.data), 0)

    def test_detail_view_returns_200(self):
        d = Dive.objects.all()[0]
        result = self.client.get(reverse('dive-detail', args=[d.id]))
        self.assertEqual(result.status_code, status.HTTP_200_OK)

    def test_detail_view_returns_expected_item(self):
        d = Dive.objects.all()[0]
        result = self.client.get(reverse('dive-detail', args=[d.id]))
        self.assertEqual(result.data['diver']['id'], d.diver.profile.id)


class DiveCreateTestCase(APITestCase):

    def setUp(self):
        self.user = UserFactory()
        #self.d = DiveFactory(diver=self.user)
        self.ds = DivesiteFactory()
        self.data = {
                'depth': faker.random_int(min=1, max=100),
                'duration': faker.random_int(min=1, max=100),
                'start_time': faker.date_time_this_year(),
                'divesite': self.ds.id
                }
        d = DiveFactory(divesite=self.ds)

    def test_unauthenticated_create_fails(self):
        count = Dive.objects.count()
        result = self.client.post(reverse('dive-list'), self.data)
        self.assertEqual(result.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Dive.objects.count(), count)

    def test_authenticated_create_succeeds(self):
        count = Dive.objects.count()
        self.assertTrue(Divesite.objects.filter(id=self.ds.id).exists())
        self.client.force_authenticate(self.user)
        result = self.client.post(reverse('dive-list'), self.data)
        self.assertEqual(result.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Dive.objects.count(), count + 1)


class DiveUpdateTestCase(APITestCase):

    def setUp(self):
        self.user = UserFactory()
        self.ds = DivesiteFactory()
        self.dive = DiveFactory(diver=self.user, divesite=self.ds)
        self.data = {'duration': timedelta(minutes=random.randint(1, 60))}
        self.url = reverse('dive-detail', args=[self.dive.id])

    def test_unauthenticated_patch_fails(self):
        result = self.client.patch(self.url, self.data)
        self.assertEqual(result.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_dive_creator_can_update(self):
        self.client.force_authenticate(self.user)
        result = self.client.patch(self.url, self.data)
        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertEqual(Dive.objects.get(id=self.dive.id).duration, self.data['duration'])

    def test_only_dive_creator_can_update(self):
        user2 = UserFactory()
        self.client.force_authenticate(user2)
        result = self.client.patch(self.url, self.data)
        self.assertEqual(result.status_code, status.HTTP_403_FORBIDDEN)

    def test_comment_can_be_edited(self):
        new_text = faker.text()
        data = {'comment': new_text}
        self.client.force_authenticate(self.user)
        result = self.client.patch(self.url, data)
        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertEqual(Dive.objects.get(id=self.dive.id).comment, new_text)


    def test_divesite_can_be_edited(self):
        data = {'divesite': self.ds.id}
        self.client.force_authenticate(self.user)
        result = self.client.patch(self.url, data)
        self.assertEqual(result.status_code, status.HTTP_200_OK)

    def test_start_time_can_be_edited_if_valid(self):
        data = {'start_time': self.dive.start_time - timedelta(minutes=-1)}
        self.client.force_authenticate(self.user)
        result = self.client.patch(self.url, data)
        self.assertEqual(result.status_code, status.HTTP_200_OK)

    def test_start_time_cannot_be_edited_if_invalid(self):
        data = {'start_time': timezone.now() + timedelta(days=1)}
        self.client.force_authenticate(self.user)
        result = self.client.patch(self.url, data)
        self.assertEqual(result.status_code, status.HTTP_400_BAD_REQUEST)

    def test_duration_can_be_edited_if_valid(self):
        new_start_time =  timezone.now() - timedelta(hours=2) # valid start time
        self.dive.start_time = new_start_time
        self.dive.save()
        self.assertEqual(Dive.objects.get(id=self.dive.id).start_time, new_start_time)
        data = {'duration': timedelta(hours=1)} # duration is valid given start time
        self.client.force_authenticate(user=self.user)
        result = self.client.patch(self.url, data)
        self.assertEqual(result.status_code, status.HTTP_200_OK)

    def test_duration_cannot_be_edited_if_invalid(self):
        new_start_time =  timezone.now() - timedelta(hours=1) # valid start time
        self.dive.start_time = new_start_time
        self.dive.save()
        self.assertEqual(Dive.objects.get(id=self.dive.id).start_time, new_start_time)
        data = {'duration': timedelta(hours=2)} # duration is invalid given start time
        self.client.force_authenticate(user=self.user)
        result = self.client.patch(self.url, data)
        self.assertEqual(result.status_code, status.HTTP_400_BAD_REQUEST)

    def test_depth_can_be_edited(self):
        new_depth = self.dive.depth + 10
        data = {'depth': new_depth}
        self.client.force_authenticate(self.user)
        result = self.client.patch(self.url, data)
        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertEqual(Dive.objects.get(id=self.dive.id).depth, new_depth)

    def test_diver_cannot_be_changed(self):
        user2 = UserFactory()
        data = {'diver': user2.profile}
        self.client.force_authenticate(user=self.user)
        result = self.client.patch(self.url, data)
        # TODO: view should throw exception instead of returning 200
        self.assertEqual(Dive.objects.get(id=self.dive.id).diver, self.user)
