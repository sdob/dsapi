from rest_framework import serializers
from profiles.models import Profile
from .models import Image, UserProfileImage


class ImageSerializer(serializers.ModelSerializer):
    # Rolling our own serializer here allows us to import from here
    # into profiles.serializers
    class MinimalProfileSerializer(serializers.ModelSerializer):
        class Meta:
            model = Profile
            fields = ('id', 'name',)

    class Meta:
        model = Image
    owner = MinimalProfileSerializer(source='owner.profile', read_only=True)
    public_id = serializers.CharField(source='image.public_id', read_only=True)
    content_type_model = serializers.ReadOnlyField(source="get_content_type_model")


class UserProfileImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfileImage
        exclude = ('user', 'id',)
    public_id = serializers.CharField(source='image.public_id', read_only=True)
