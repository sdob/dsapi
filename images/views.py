from django.shortcuts import render
from rest_framework import mixins, viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from divesites.models import Compressor, Divesite, Slipway
from divesites.permissions import IsOwnerOrReadOnly
from .models import CompressorImage, DivesiteImage, SlipwayImage
from .serializers import CompressorImageSerializer, DivesiteImageSerializer, SlipwayImageSerializer

class CompressorImageViewSet(viewsets.GenericViewSet,
        mixins.CreateModelMixin,
        mixins.RetrieveModelMixin,
        mixins.UpdateModelMixin,
        mixins.DestroyModelMixin):
    permission_classes = (IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly,)
    queryset = CompressorImage.objects.all()
    serializer_class = CompressorImageSerializer

    def check_compressor_ownership(self, compressor):
        user = self.request.user
        if 'is_header_image' in self.request.data and not user == compressor.owner:
            raise PermissionDenied()

    def perform_create(self, serializer):
        owner = self.request.user
        # Pull the compressor ID out of the request data
        compressor = Compressor.objects.get(id=self.request.data['compressor'])
        # Check site ownership
        self.check_compressor_ownership(compressor)
        # Save the instance
        instance = serializer.save(owner=owner, compressor=compressor)

    def perform_update(self, serializer):
        compressor = Compressor.objects.get(id=self.request.data['compressor'])
        # Check ownership
        self.check_compressor_ownership(compressor)
        serializer.save()


class DivesiteImageViewSet(viewsets.GenericViewSet,
        mixins.CreateModelMixin,
        mixins.RetrieveModelMixin,
        mixins.UpdateModelMixin,
        mixins.DestroyModelMixin):
    permission_classes = (IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly,)
    queryset = DivesiteImage.objects.all()
    serializer_class = DivesiteImageSerializer

    def check_divesite_ownership(self, divesite):
        user = self.request.user
        if 'is_header_image' in self.request.data and not user == divesite.owner:
            raise PermissionDenied()

    def perform_create(self, serializer):
        owner = self.request.user
        # Pull the compressor ID out of the request data
        divesite = Divesite.objects.get(id=self.request.data['divesite'])
        # Check ownership
        self.check_divesite_ownership(divesite)
        # Save the instance
        instance = serializer.save(owner=owner, divesite=divesite)

    def perform_update(self, serializer):
        divesite = Divesite.objects.get(id=self.request.data['divesite'])
        # Check ownership
        self.check_divesite_ownership(divesite)
        serializer.save()


class SlipwayImageViewSet(viewsets.GenericViewSet,
        mixins.CreateModelMixin,
        mixins.RetrieveModelMixin,
        mixins.UpdateModelMixin,
        mixins.DestroyModelMixin):
    permission_classes = (IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly,)
    queryset = SlipwayImage.objects.all()
    serializer_class = SlipwayImageSerializer

    def check_slipway_ownership(self, slipway):
        user = self.request.user
        if 'is_header_image' in self.request.data and not user == slipway.owner:
            raise PermissionDenied()

    def perform_create(self, serializer):
        owner = self.request.user
        slipway_id = self.request.data['slipway']
        slipway = Slipway.objects.get(id=slipway_id)
        # Check ownership
        self.check_slipway_ownership(slipway)
        # Save the instance
        instance = serializer.save(owner=owner, slipway=slipway)

    def perform_update(self, serializer):
        slipway = Slipway.objects.get(id=self.request.data['slipway'])
        # Check ownership
        self.check_slipway_ownership(slipway)
        serializer.save()
