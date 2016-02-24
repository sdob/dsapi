from django.core.management.base import NoArgsCommand
from dsapi import urls

class Command(NoArgsCommand):
    help = 'Show all registered URLs'
    def handle_noargs(self, **options):
        def show_urls(urllist, depth=0):
            for entry in urllist:
                print(' ' * depth, entry.regex.pattern)
                if hasattr(entry, 'url_patterns'):
                    show_urls(entry.url_patterns, depth + 1)

        show_urls(urls.urlpatterns)
