from django.apps import AppConfig


class DivesitesConfig(AppConfig):
    name = 'divesites'

    def ready(self):
        from actstream import registry
        registry.register(self.get_model('Compressor'))
        registry.register(self.get_model('Divesite'))
        registry.register(self.get_model('Dive'))
        registry.register(self.get_model('Slipway'))

