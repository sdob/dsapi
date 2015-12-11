from rest_framework.serializers import ModelSerializer
from .models import User
from profiles.serializers import ProfileSerializer

class UserSerializer(ModelSerializer):
    profile = ProfileSerializer(read_only=True)
    class Meta:
        model = User
        fields = ('profile',)
