from django.contrib.auth import login
from allauth.socialaccount.providers.facebook.views import FacebookOAuth2Adapter
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from rest_auth.registration.views import SocialLoginView

from dsapi import settings

# These custom classes with no-argument initializers
# fix a bug with django-rest-auth and django-allauth > 0.25;
# see the following:
# https://github.com/Tivix/django-rest-auth/issues/197
# http://stackoverflow.com/questions/36317325/django-rest-auth-facebooklogin-view-missing-1-required-positional-argument-r
class FacebookOAuth2AdapterCustom(FacebookOAuth2Adapter):
    def __init__(self):
        pass


class GoogleOAuth2AdapterCustom(GoogleOAuth2Adapter):
    def __init__(self):
        pass


class FacebookLogin(SocialLoginView):
    adapter_class = FacebookOAuth2AdapterCustom
    callback_url = settings.FACEBOOK_AUTH_CALLBACK_URL
    client_class = OAuth2Client


class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2AdapterCustom
    callback_url = settings.GOOGLE_AUTH_CALLBACK_URL
    client_class = OAuth2Client
    # Try overriding social login
    # see: https://www.bountysource.com/issues/10278183-social-rest-auth-with-rest_session_login-true
    def login(self):
        self.user = self.serializer.validated_data['user']
        self.token, created = self.token_model.objects.get_or_create(
                user = self.user)
        if getattr(settings, 'REST_SESSION_LOGIN', True):
            if not hasattr(self.user, 'backend'):
                self.user.backend = 'django.contrib.auth.backends.ModelBackend'
            login(self.request, self.user)
