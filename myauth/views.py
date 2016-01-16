from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken as ObtainAuthTokenBase
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import User
from profiles.models import Profile

class ObtainAuthToken(ObtainAuthTokenBase):

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key, 'user': user.profile.id})


class CreateUserView(APIView):

    def post(self, request):
        # Check whether a user exists with this email address
        if User.objects.filter(email=request.data['email']).exists():
                return Response(
                        data={
                            'message': '"%s" is already registered.' % request.data['email']
                            },
                        status=status.HTTP_400_BAD_REQUEST
                        )
        # Otherwise, create a user
        user = User.objects.create_user(
                email=request.data['email'],
                password=request.data['password']
                )
        if request.data.has_key('full_name'):
            # Set the user's full name
            user.profile.name = request.data['full_name']
            user.profile.save()
        # Respond with a token
        token = Token.objects.get(user=user)
        return Response({'token': token.key}, status=status.HTTP_201_CREATED)


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

register = CreateUserView.as_view()
check_token = CheckToken.as_view()
obtain_auth_token = ObtainAuthToken.as_view()
