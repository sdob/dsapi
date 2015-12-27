from django.core.exceptions import ValidationError
from rest_framework import viewsets
from rest_framework.decorators import detail_route, list_route
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from .serializers import DiveSerializer, DivesiteSerializer
from .models import Dive, Divesite
from .permissions import IsDiverOrReadOnly, IsOwnerOrReadOnly
import activity.serializers

class DivesiteViewSet(viewsets.ModelViewSet):

    permission_classes = (IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly,)
    queryset = Divesite.objects.all()
    serializer_class = DivesiteSerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

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

    from django.views.defaults import bad_request
    def create(self, request, *args, **kwargs):
        try:
            return super(viewsets.ModelViewSet, self).create(request, *args, **kwargs)
        except ValidationError:
            return bad_request(request)

    def perform_create(self, serializer):
        # Unless we explicitly set the divesite ID here, we get an IntegrityError (?)
        serializer.save(diver=self.request.user, divesite=Divesite.objects.get(id=self.request.data['divesite']))
