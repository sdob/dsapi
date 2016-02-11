from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from haversine import haversine
from rest_framework import mixins
from rest_framework import viewsets
from rest_framework.decorators import detail_route, list_route
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from .serializers import CompressorSerializer, DiveSerializer, DiveListSerializer,  DivesiteSerializer, DivesiteListSerializer, SlipwaySerializer
from .models import Compressor, Dive, Divesite, Slipway
from .permissions import IsDiverOrReadOnly, IsOwnerOrReadOnly
from comments.models import DivesiteComment, SlipwayComment, CompressorComment
from comments.serializers import DivesiteCommentSerializer, CompressorCommentSerializer, SlipwayCommentSerializer 

class DivesiteViewSet(viewsets.ModelViewSet):


    permission_classes = (IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly,)
    queryset = Divesite.objects.all()
    serializer_class = DivesiteSerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def list(self, request):
        queryset = self.get_queryset()
        serializer = DivesiteListSerializer(queryset, many=True)
        return Response(serializer.data)

    @detail_route(methods=['get'])
    def comments(self, request, pk):
        queryset = DivesiteComment.objects.filter(divesite=self.get_object())
        serializer = DivesiteCommentSerializer(queryset, many=True)
        return Response(serializer.data)

    @detail_route(methods=['get'])
    def dives(self, request, pk):
        divesite = self.get_object()
        queryset = Dive.objects.filter(divesite=divesite)
        # Use DiveListSerializer since we don't need more than a
        # MinimalProfileSerializer and a primary key for the divesite
        serializer = DiveListSerializer(queryset, many=True)
        return Response(serializer.data)

    @detail_route(methods=['get'])
    def nearby_slipways(self, request, pk):
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
        # TODO: sort on Haversine distance
        serializer = SlipwaySerializer(slipways, many=True)
        return Response(serializer.data)


class DiveViewSet(viewsets.GenericViewSet,
        # Don't mix in ListModelMixin: we don't want an API endpoint for it
        mixins.CreateModelMixin,
        mixins.RetrieveModelMixin,
        mixins.UpdateModelMixin,
        mixins.DestroyModelMixin):

    permission_classes = (IsAuthenticatedOrReadOnly,IsDiverOrReadOnly,)
    queryset = Dive.objects.all()
    serializer_class = DiveSerializer

    def perform_create(self, serializer):
        # Unless we explicitly set the divesite ID here, we get an IntegrityError (?)
        serializer.save(diver=self.request.user, divesite=Divesite.objects.get(id=self.request.data['divesite']))


class CompressorViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly,)
    queryset = Compressor.objects.all()
    serializer_class = CompressorSerializer

    def perform_create(self, serializer):
        # Set the owner
        serializer.save(owner=self.request.user)

    @detail_route(methods=['get'])
    def comments(self, request, pk):
        queryset = CompressorComment.objects.filter(compressor=self.get_object())
        serializer = CompressorCommentSerializer(queryset, many=True)
        return Response(serializer.data)


class SlipwayViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly,)
    queryset = Slipway.objects.all()
    serializer_class = SlipwaySerializer

    def perform_create(self, serializer):
        # Set the owner
        serializer.save(owner=self.request.user)

    @detail_route(methods=['get'])
    def comments(self, request, pk):
        queryset = SlipwayComment.objects.filter(slipway=self.get_object())
        serializer = SlipwayCommentSerializer(queryset, many=True)
        return Response(serializer.data)
