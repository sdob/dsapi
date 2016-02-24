from actstream import action
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from haversine import haversine
from rest_framework import mixins
from rest_framework import viewsets
from rest_framework import status
from rest_framework.decorators import detail_route, list_route
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from .serializers import CompressorSerializer, DiveSerializer, DiveListSerializer,  DivesiteSerializer, DivesiteListSerializer, SlipwaySerializer
from .models import Compressor, Dive, Divesite, Slipway
from .permissions import IsDiverOrReadOnly, IsOwnerOrReadOnly
from comments.models import DivesiteComment, SlipwayComment, CompressorComment
from comments.serializers import DivesiteCommentSerializer, CompressorCommentSerializer, SlipwayCommentSerializer 
from images.models import Image
from images.serializers import ImageSerializer

class DivesiteViewSet(viewsets.ModelViewSet):

    permission_classes = (IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly,)
    queryset = Divesite.objects.all()
    serializer_class = DivesiteSerializer

    def perform_create(self, serializer):
        # Get the user from the request
        user = self.request.user
        instance = serializer.save(owner=user)

    def list(self, request):
        queryset = self.get_queryset()
        serializer = DivesiteListSerializer(queryset, many=True)
        return Response(serializer.data)

    @detail_route(methods=['get'])
    def comments(self, request, pk):
        # Return comments on this divesite
        queryset = DivesiteComment.objects.filter(divesite=self.get_object())
        serializer = DivesiteCommentSerializer(queryset, many=True)
        return Response(serializer.data)

    @detail_route(methods=['get'])
    def dives(self, request, pk):
        # Return dives at this divesite
        divesite = self.get_object()
        queryset = Dive.objects.filter(divesite=divesite)
        # Use DiveListSerializer since we don't need more than a
        # MinimalProfileSerializer and a primary key for the divesite
        serializer = DiveListSerializer(queryset, many=True)
        return Response(serializer.data)

    @detail_route(methods=['get'])
    def nearby_slipways(self, request, pk):
        # Return nearby slipways for this divesite
        NEARBY_SLIPWAY_KM_LIMIT = 15
        # XXX: this is going to hit the DB for *all* slipways, then
        # sort them on haversine, then return the top n results.
        # In other words, it's an expensive query.
        # With GeoDjango there's probably a better way to do it,
        # but that'll require SaaS support for GeoDjango
        divesite = get_object_or_404(self.get_queryset(), pk=pk)
        slipways = Slipway.objects.all()
        # Sort the slipways on Haversine distance from this
        # divesite
        key = lambda slipway: haversine(
                (divesite.latitude, divesite.longitude),
                (slipway.latitude, slipway.longitude)
                )
        slipways = [slipway for slipway in sorted(slipways, key=key) \
                if haversine(
                (divesite.latitude, divesite.longitude),
                (slipway.latitude, slipway.longitude)
                    ) <= NEARBY_SLIPWAY_KM_LIMIT]
        serializer = SlipwaySerializer(slipways, many=True)
        return Response(serializer.data)


class DiveViewSet(viewsets.GenericViewSet,
        # Don't mix in ListModelMixin: we don't want an API endpoint for
        # it (there's no use-case for 'list all dives')
        mixins.CreateModelMixin,
        mixins.RetrieveModelMixin,
        mixins.UpdateModelMixin,
        mixins.DestroyModelMixin):

    permission_classes = (IsAuthenticatedOrReadOnly,IsDiverOrReadOnly,)
    queryset = Dive.objects.all()
    serializer_class = DiveSerializer

    def perform_create(self, serializer):
        # Get the divesite instance from the request
        divesite = Divesite.objects.get(id=self.request.data['divesite'])
        # Get the user from the request
        user = self.request.user
        # Unless we explicitly set the divesite ID here, we get an IntegrityError (?)
        instance = serializer.save(diver=user, divesite=divesite)


class CompressorViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly,)
    queryset = Compressor.objects.all()
    serializer_class = CompressorSerializer

    def perform_create(self, serializer):
        # Get the user from the request
        owner = self.request.user
        # Save the instance
        instance = serializer.save(owner=owner)

    @detail_route(methods=['get'])
    def comments(self, request, pk):
        # Return comments on this compressor
        queryset = CompressorComment.objects.filter(compressor=self.get_object())
        serializer = CompressorCommentSerializer(queryset, many=True)
        return Response(serializer.data)


class SlipwayViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly,)
    queryset = Slipway.objects.all()
    serializer_class = SlipwaySerializer

    def perform_create(self, serializer):
        # Get the user from the request
        owner = self.request.user
        # Save the instance
        instance = serializer.save(owner=owner)

    @detail_route(methods=['get'])
    def comments(self, request, pk):
        queryset = SlipwayComment.objects.filter(slipway=self.get_object())
        serializer = SlipwayCommentSerializer(queryset, many=True)
        return Response(serializer.data)
