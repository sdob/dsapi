from rest_framework import serializers
from profiles.serializers import MinimalProfileSerializer
from .models import Image, UserProfileImage

class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
    owner = MinimalProfileSerializer(source='owner.profile', read_only=True)


class UserProfileImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfileImage
        exclude = ('user', 'id',)
    public_id = serializers.CharField(source='image.public_id', read_only=True)
