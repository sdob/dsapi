from django.shortcuts import render
from rest_framework import mixins, viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from divesites.permissions import IsOwnerOrReadOnly
from .models import Image

class ImageViewSet(viewsets.GenericViewSet,
        mixins.CreateModelMixin,
        mixins.RetrieveModelMixin,
        mixins.UpdateModelMixin,
        mixins.DestroyModelMixin):
    permission_classes = (IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly,)
    queryset = Image.objects.all()
    # serializer_class = CompressorImageSerializer

    # TODO: check ownership of associated item before setting this as
    # the header image
    # def check_compressor_ownership(self, compressor):
        # user = self.request.user
        # if 'is_header_image' in self.request.data and not user == compressor.owner:
            # raise PermissionDenied()

    def perform_create(self, serializer):
        owner = self.request.user
        # Pull the compressor ID out of the request data
        # TODO: Make this generic
        # compressor = Compressor.objects.get(id=self.request.data['compressor'])
        # Check site ownership
        # self.check_compressor_ownership(compressor)
        # Save the instance
        instance = serializer.save(owner=owner, compressor=compressor)

    def perform_update(self, serializer):
        # TODO: make this generic
        # compressor = Compressor.objects.get(id=self.request.data['compressor'])
        # Check ownership
        # self.check_compressor_ownership(compressor)
        serializer.save()
