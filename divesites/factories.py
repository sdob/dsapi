import factory
import random

from datetime import timedelta
from django.utils import timezone
from faker import Factory as FakerFactory
from faker.generator import random
from . import models
from myauth.factories import UserFactory

faker = FakerFactory.create()

class DivesiteFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Divesite

    name = factory.Sequence(lambda n: 'Divesite {0}'.format(n))
    latitude = factory.Faker('latitude')
    longitude = factory.Faker('longitude')
    owner = factory.SubFactory(UserFactory)
    @factory.lazy_attribute
    def level(self):
        return faker.random_int(min=0, max=2)


class DiveFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Dive

    divesite = factory.SubFactory(DivesiteFactory)
    diver = factory.SubFactory(UserFactory)
    @factory.lazy_attribute
    def depth(self):
        return random.randint(10, 100)
    @factory.lazy_attribute
    def start_time(self):
        # TODO: ensure that by default this is at least one day before today
        dt = faker.date_time_this_year(before_now=True, after_now=False) - timedelta(days=2)
        tz = timezone.get_default_timezone()
        aware = timezone.make_aware(dt, tz)
        return aware
    @factory.lazy_attribute
    def duration(self):
        seconds = random.randint(1, 60) * 60
        return timedelta(seconds=seconds)


class CompressorFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Compressor

    name = factory.Sequence(lambda n: 'Slipway {0}'.format(n))
    latitude = factory.Faker('latitude')
    longitude = factory.Faker('longitude')
    owner = factory.SubFactory(UserFactory)
    description = factory.Faker('text')


class SlipwayFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Slipway

    name = factory.Sequence(lambda n: 'Slipway {0}'.format(n))
    latitude = factory.Faker('latitude')
    longitude = factory.Faker('longitude')
    owner = factory.SubFactory(UserFactory)
    description = factory.Faker('text')
