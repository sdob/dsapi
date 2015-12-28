from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import User
from profiles.models import Profile

class CheckToken(APIView):

    def post(self, request):
        default_bad_response = Response(status=status.HTTP_401_UNAUTHORIZED)
        if not ('token' in request.data.keys() and 'user' in request.data.keys()):
            return default_bad_response
        token = request.data['token']
        profile_id = request.data['user']
        try:
            profile = Profile.objects.get(id=profile_id)
            if Token.objects.get(user=profile.user).key == token:
                return Response(status=status.HTTP_200_OK)
            return default_bad_response
        except Profile.DoesNotExist:
            return default_bad_response

check_token = CheckToken.as_view()
