from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from haversine import haversine
from rest_framework import viewsets
from rest_framework.decorators import detail_route, list_route
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from .serializers import CompressorSerializer, DiveSerializer, DivesiteSerializer, DivesiteListSerializer, SlipwaySerializer
from .models import Compressor, Dive, Divesite, Slipway
from .permissions import IsDiverOrReadOnly, IsOwnerOrReadOnly
from activity.models import DiveLog
from activity.serializers import DiveLogSerializer

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
    def dives(self, request, pk):
        divesite = self.get_object()
        dives = Dive.objects.filter(divesite=divesite)
        serializer = DiveSerializer(dives, many=True)
        return Response(serializer.data)

    @detail_route(methods=['get'])
    def recent_dives(self, request, pk):
        queryset = Divesite.objects.all()
        max_items = 10
        divesite = get_object_or_404(queryset, pk=pk)
        dive_logs = DiveLog.objects.filter(dive__divesite=divesite).order_by('-creation_date')[:max_items]
        serializer = DiveLogSerializer(dive_logs, many=True)
        return Response(serializer.data)
        #activities = Activity.objects.filter(divesite=divesite).select_subclasses()[:max_items]
        #data = [activity.serializers.serializer_factory

    @detail_route(methods=['get'])
    def nearby_slipways(self, request, pk):
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
                    ) <= 5000]
        print "returning Slipways: %d" % len(slipways)
        # TODO: sort on Haversine distance
        serializer = SlipwaySerializer(slipways, many=True)
        print serializer.data
        return Response(serializer.data)


class DiveViewSet(viewsets.ModelViewSet):

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


class SlipwayViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly,)
    queryset = Slipway.objects.all()
    serializer_class = SlipwaySerializer

    def perform_create(self, serializer):
        # Set the owner
        serializer.save(owner=self.request.user)
