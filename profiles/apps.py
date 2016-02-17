from django.apps import AppConfig

class ProfilesConfig(AppConfig):
    name = 'profiles'

    def ready(self):
        from actstream import registry
        registry.register(self.get_model('Profile'))
