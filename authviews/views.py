from django.contrib.auth import login
from allauth.socialaccount.providers.facebook.views import FacebookOAuth2Adapter
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from rest_auth.registration.views import SocialLoginView

from dsapi import settings

class FacebookLogin(SocialLoginView):
    adapter_class = FacebookOAuth2Adapter
    callback_url = 'https://dsfe.herokuapp.com'
    client_class = OAuth2Client


class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    callback_url = 'https://dsfe.herokuapp.com'
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
