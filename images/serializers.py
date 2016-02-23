from rest_framework import serializers

from .models import CompressorImage, DivesiteImage, SlipwayImage
from divesites.serializers import CompressorSerializer, DivesiteSerializer, SlipwaySerializer
from profiles.serializers import MinimalProfileSerializer

class BaseImageSerializer(serializers.ModelSerializer):
    owner = MinimalProfileSerializer(source='owner.profile', read_only=True)

class CompressorImageSerializer(BaseImageSerializer):
    class Meta:
        model = CompressorImage
    compressor = CompressorSerializer(read_only=True)


class DivesiteImageSerializer(BaseImageSerializer):
    class Meta:
        model = DivesiteImage
    divesite = DivesiteSerializer(read_only=True)


class SlipwayImageSerializer(BaseImageSerializer):
    class Meta:
        model = SlipwayImage
    slipway = SlipwaySerializer(read_only=True)
