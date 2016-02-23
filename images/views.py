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
        owner = self.request.user
        # If we're trying to set the header and we don't own the compressor, raise an exception
        is_header_image = self.request.data['is_header_image']
        if is_header_image and not owner == compressor.owner:
            raise PermissionDenied()

    def perform_create(self, serializer):
        owner = self.request.user
        # Pull the compressor ID out of the request data
        compressor = Compressor.objects.get(id=self.request.data['compressor'])
        # Check site ownership
        self.check_compressor_ownership(compressor)
        # Save the instance
        instance = serializer.save(owner=owner, compressor=compressor)


class DivesiteImageViewSet(viewsets.GenericViewSet,
        mixins.CreateModelMixin,
        mixins.RetrieveModelMixin,
        mixins.UpdateModelMixin,
        mixins.DestroyModelMixin):
    permission_classes = (IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly,)
    queryset = DivesiteImage.objects.all()
    serializer_class = DivesiteImageSerializer

    def check_divesite_ownership(self, divesite):
        owner = self.request.user
        # If we're trying to set the header and we don't own the divesite, raise an exception
        is_header_image = self.request.data['is_header_image']
        if is_header_image and not owner == divesite.owner:
            raise PermissionDenied()

    def perform_create(self, serializer):
        owner = self.request.user
        # Pull the compressor ID out of the request data
        divesite = Divesite.objects.get(id=self.request.data['divesite'])
        # Check ownership
        self.check_divesite_ownership(divesite)
        # Save the instance
        instance = serializer.save(owner=owner, divesite=divesite)


class SlipwayImageViewSet(viewsets.GenericViewSet,
        mixins.CreateModelMixin,
        mixins.RetrieveModelMixin,
        mixins.UpdateModelMixin,
        mixins.DestroyModelMixin):
    permission_classes = (IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly,)
    queryset = SlipwayImage.objects.all()
    serializer_class = SlipwayImageSerializer

    def check_slipway_ownership(self, slipway):
        owner = self.request.user
        # If we're trying to set the header and we don't own the divesite, raise an exception
        is_header_image = self.request.data['is_header_image']
        if is_header_image and not owner == slipway.owner:
            raise PermissionDenied()

    def perform_create(self, serializer):
        owner = self.request.user
        # Pull the compressor ID out of the request data
        slipway = Slipway.objects.get(id=self.request.data['slipway'])
        # Check ownership
        self.check_slipway_ownership(slipway)
        # Save the instance
        instance = serializer.save(owner=owner, slipway=slipway)

    def perform_update(self, serializer):
        # Check ownership
        self.check_slipway_ownership(slipway)
        return super(self, mixins.UpdateModelMixin).perform_update(serializer)
