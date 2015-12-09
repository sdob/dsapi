import factory
from . import models

class UserFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.User

    email=factory.Faker('email')
    password=factory.Faker('password')

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        manager = cls._get_manager(model_class)
        return manager.create_user(*args, **kwargs)
