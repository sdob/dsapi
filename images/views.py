from django.http import HttpResponseBadRequest
from django.shortcuts import render
from rest_framework import mixins, viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from divesites.models import Compressor, Divesite, Slipway
from divesites.permissions import IsOwnerOrReadOnly
from .models import Image
from .serializers import ImageSerializer

class ImageViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    queryset = Image.objects.all()
    serializer_class = ImageSerializer

    # TODO: check ownership of associated item before setting this as
    # the header image
    # def check_compressor_ownership(self, compressor):
        # user = self.request.user
        # if 'is_header_image' in self.request.data and not user == compressor.owner:
            # raise PermissionDenied()

    def perform_create(self, serializer):
        print('PERFORM_CREATE')
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
