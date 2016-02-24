from django.apps import AppConfig


class ImagesConfig(AppConfig):
    name = 'images'

    def ready(self):
        from actstream import registry
        registry.register(self.get_model('Image'))
