from django.apps import AppConfig

# Jump through the requisite hoops to register User objects with actstream
class DjangoContribAuthConfig(AppConfig):
    name = 'django.contrib.auth'

    def ready(self):
        from actstream import registry
        registry.register(self.get_model('User'))
