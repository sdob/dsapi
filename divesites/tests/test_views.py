from django.core.urlresolvers import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from divesites import factories, models

NUM_SITES = 4
NUM_DIVES = 10

class DivesiteSafeViewsTestCase(APITestCase):

    @classmethod
    def setUpClass(cls):
        super(DivesiteSafeViewsTestCase, cls).setUpClass()
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
        ds = models.Divesite.objects.all()[0]
        result = self.client.get(reverse('divesite-detail', args=[ds.id]))
        self.assertEqual(result.status_code, status.HTTP_200_OK)

    def test_detail_view_returns_expected_item(self):
        ds = models.Divesite.objects.all()[0]
        data = self.client.get(reverse('divesite-detail', args=[ds.id])).data
        self.assertEqual(data['name'], ds.name)
        self.assertEqual(data['id'], str(ds.id))
        self.assertEqual(str(data['owner']), str(ds.owner.id))

class DiveSafeViewsTestCase(APITestCase):

    #@classmethod
    #def setUpClass(cls):
    def setUp(self):
        self.ds0, self.ds1 = factories.DivesiteFactory(), factories.DivesiteFactory()
        for _ in xrange(NUM_DIVES):
            d = factories.DiveFactory(divesite=self.ds0)

    def test_list_of_related_dives_returns_200(self):
        result = self.client.get(reverse('divesite-dives', args=[self.ds0.id]))
        self.assertEqual(result.status_code, status.HTTP_200_OK)
