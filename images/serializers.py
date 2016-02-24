from rest_framework import serializers
from profiles.serializers import MinimalProfileSerializer
from .models import Image

class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
    owner = MinimalProfileSerializer(source='owner.profile', read_only=True)
