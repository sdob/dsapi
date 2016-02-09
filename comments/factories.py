import factory
import random


from divesites.factories import DivesiteFactory, UserFactory
from .models import DivesiteComment

class DivesiteCommentFactory(factory.DjangoModelFactory):
    class Meta:
        model = DivesiteComment

    owner = factory.SubFactory(UserFactory)
    divesite = factory.SubFactory(DivesiteFactory)
    text = factory.Faker('text')
