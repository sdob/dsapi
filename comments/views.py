from django.shortcuts import render
from rest_framework import mixins, viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from divesites.models import Divesite, Compressor, Slipway
from divesites.permissions import IsOwnerOrReadOnly
from .models import DivesiteComment, SlipwayComment, CompressorComment
from .serializers import DivesiteCommentSerializer, SlipwayCommentSerializer, CompressorCommentSerializer

# Create your views here.
class DivesiteCommentViewSet(viewsets.GenericViewSet,
        mixins.CreateModelMixin,
        mixins.RetrieveModelMixin,
        mixins.UpdateModelMixin,
        mixins.DestroyModelMixin):

    permission_classes = (IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly,)
    queryset = DivesiteComment.objects.all()
    serializer_class = DivesiteCommentSerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user, divesite=Divesite.objects.get(id=self.request.data['divesite']))
