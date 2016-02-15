from django.apps import AppConfig


class CommentsConfig(AppConfig):
    name = 'comments'
    def ready(self):
        from actstream import registry
        registry.register(self.get_model('CompressorComment'))
        registry.register(self.get_model('SlipwayComment'))
        registry.register(self.get_model('DivesiteComment'))
