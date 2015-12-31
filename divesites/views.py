from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.decorators import detail_route, list_route
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from .serializers import DiveSerializer, DivesiteSerializer, DivesiteListSerializer
from .models import Dive, Divesite
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


class DiveViewSet(viewsets.ModelViewSet):

    permission_classes = (IsAuthenticatedOrReadOnly,IsDiverOrReadOnly,)
    queryset = Dive.objects.all()
    serializer_class = DiveSerializer

    def perform_create(self, serializer):
        # Unless we explicitly set the divesite ID here, we get an IntegrityError (?)
        serializer.save(diver=self.request.user, divesite=Divesite.objects.get(id=self.request.data['divesite']))
