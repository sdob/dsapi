from django.shortcuts import render
from rest_framework import mixins, viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from divesites.models import Divesite, Compressor, Slipway
from divesites.permissions import IsOwnerOrReadOnly
from .models import DivesiteComment, SlipwayComment, CompressorComment
from .serializers import DivesiteCommentSerializer, SlipwayCommentSerializer, CompressorCommentSerializer

# Viewsets for comments.
class CompressorCommentViewSet(viewsets.GenericViewSet,
        mixins.CreateModelMixin,
        mixins.RetrieveModelMixin,
        mixins.UpdateModelMixin,
        mixins.DestroyModelMixin):

    permission_classes = (IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly,)
    queryset = CompressorComment.objects.all()
    serializer_class = CompressorCommentSerializer

    def perform_create(self, serializer):
        # Pull the slipway ID out of the request data
        serializer.save(owner=self.request.user, compressor=Compressor.objects.get(id=self.request.data['compressor']))


class DivesiteCommentViewSet(viewsets.GenericViewSet,
        mixins.CreateModelMixin,
        mixins.RetrieveModelMixin,
        mixins.UpdateModelMixin,
        mixins.DestroyModelMixin):

    permission_classes = (IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly,)
    queryset = DivesiteComment.objects.all()
    serializer_class = DivesiteCommentSerializer

    def perform_create(self, serializer):
        # Pull the divesite ID out of the request data
        serializer.save(owner=self.request.user, divesite=Divesite.objects.get(id=self.request.data['divesite']))


class SlipwayCommentViewSet(viewsets.GenericViewSet,
        mixins.CreateModelMixin,
        mixins.RetrieveModelMixin,
        mixins.UpdateModelMixin,
        mixins.DestroyModelMixin):

    permission_classes = (IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly,)
    queryset = SlipwayComment.objects.all()
    serializer_class = SlipwayCommentSerializer

    def perform_create(self, serializer):
        # Pull the slipway ID out of the request data
        serializer.save(owner=self.request.user, slipway=Slipway.objects.get(id=self.request.data['slipway']))
