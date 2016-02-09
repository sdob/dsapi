import factory
import random

from datetime import date, time, timedelta
from django.utils import timezone
from unittest.mock import patch
from faker import Factory as FakerFactory
from faker.generator import random
from . import models
from django.contrib.auth.models import User

faker = FakerFactory.create()

class UserFactory(factory.DjangoModelFactory):
    class Meta:
        model = User
    username = factory.Faker('user_name')
    password = factory.Faker('password')

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        manager = cls._get_manager(model_class)
        return manager.create_user(*args, **kwargs)

@patch('models.Divesite.get_geocoding_data')
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
    def date(self):
        dt = faker.date_time_this_year(before_now=True, after_now=False) - timedelta(days=2)
        return date(year=dt.year, month=dt.month, day=dt.day)
    @factory.lazy_attribute
    def time(self):
        dt = faker.date_time_this_year(before_now=True, after_now=False) - timedelta(days=2)
        tz = timezone.get_default_timezone()
        return timezone.make_aware(time(hour=dt.hour, minute=dt.minute, second=dt.second), tz)
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
