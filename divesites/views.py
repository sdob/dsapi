from rest_framework import viewsets
from rest_framework.decorators import detail_route, list_route
from rest_framework.response import Response
from . import models, serializers

class DivesiteViewSet(viewsets.ModelViewSet):
    queryset = models.Divesite.objects.all()
    serializer_class = serializers.DivesiteSerializer

    @detail_route
    def dives(self, request, pk):
        divesite = self.get_object()
        #print divesite
        dives = Dive.objects.filter(divesite=divesite)
        s = serializers.DiveSerializer(dives, many=True)
        return Response(s.data)
