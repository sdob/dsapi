from rest_framework import serializers
from profiles.serializers import MinimalProfileSerializer
from .models import DivesiteComment, SlipwayComment, CompressorComment

class DivesiteCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = DivesiteComment
    owner = MinimalProfileSerializer(source='owner.profile', read_only=True)

class SlipwayCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = SlipwayComment
    owner = MinimalProfileSerializer(source='owner.profile', read_only=True)

class CompressorCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompressorComment
    owner = MinimalProfileSerializer(source='owner.profile', read_only=True)
