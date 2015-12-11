from rest_framework import viewsets
from rest_framework.decorators import detail_route, list_route
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from .serializers import CompactDivesiteSerializer, DiveSerializer, DivesiteSerializer
from .models import Dive, Divesite
from .permissions import IsDiverOrReadOnly, IsOwnerOrReadOnly

class DivesiteViewSet(viewsets.ModelViewSet):

    permission_classes = (IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly,)
    queryset = Divesite.objects.all()
    serializer_class = DivesiteSerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def list(self, request):
        queryset = self.get_queryset()
        serializer = CompactDivesiteSerializer(queryset, many=True)
        return Response(serializer.data)

    @detail_route(methods=['get'])
    def dives(self, request, pk):
        divesite = self.get_object()
        dives = Dive.objects.filter(divesite=divesite)
        serializer = DiveSerializer(dives, many=True)
        return Response(serializer.data)


class DiveViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticatedOrReadOnly,IsDiverOrReadOnly,)
    queryset = Dive.objects.all()
    serializer_class = DiveSerializer

    def perform_create(self, serializer):
        serializer.save(diver=self.request.user)
