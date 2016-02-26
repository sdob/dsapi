from django.http import HttpResponseBadRequest
from django.shortcuts import render
from rest_framework import mixins, viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from divesites.models import Compressor, Divesite, Slipway
from divesites.permissions import IsOwnerOrReadOnly
from .models import Image
from .serializers import ImageSerializer

class ImageViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    queryset = Image.objects.all()
    serializer_class = ImageSerializer

    # Here's where it gets messy w.r.t. divesites/slipways/compressor
    def list(self, request, divesite_pk=None, slipway_pk=None, compressor_pk=None):
        queryset = self.get_queryset()
        if compressor_pk is not None:
            print('looking for images for compressor with pk: %s' % compressor_pk)
            images = Compressor.objects.get(id=compressor_pk).images.all()
        elif divesite_pk is not None:
            print('looking for images for divesite with pk: %s' % divesite_pk)
            images = Divesite.objects.get(id=divesite_pk).images.all()
        elif slipway_pk is not None:
            print('looking for images for slipway with pk: %s' % slipway_pk)
            images = Slipway.objects.get(id=slipway_pk).images.all()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


    # TODO: check ownership of associated item before setting this as
    # the header image
    # def check_compressor_ownership(self, compressor):
        # user = self.request.user
        # if 'is_header_image' in self.request.data and not user == compressor.owner:
            # raise PermissionDenied()

    def perform_create(self, serializer):
        # Set the owner as the requesting user
        owner = self.request.user
        # Save the instance
        instance = serializer.save(owner=owner)

    def perform_update(self, serializer):
        # TODO: make this generic
        # compressor = Compressor.objects.get(id=self.request.data['compressor'])
        # TODO: Check site ownership
        # self.check_compressor_ownership(compressor)
        serializer.save()
