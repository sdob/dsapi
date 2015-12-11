from django.shortcuts import render, get_object_or_404
from rest_framework import mixins
from rest_framework import viewsets
from rest_framework.decorators import detail_route
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .models import Profile
from .permissions import IsProfileOwnerOrReadOnly
from .serializers import ProfileSerializer
from divesites.models import Dive, Divesite
from divesites.serializers import DiveSerializer, DivesiteSerializer

class ProfileViewSet(viewsets.GenericViewSet,
        mixins.UpdateModelMixin,
        mixins.RetrieveModelMixin):

    permission_classes = (IsAuthenticatedOrReadOnly, IsProfileOwnerOrReadOnly)
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer

    @detail_route(methods=['get'])
    def dives(self, request, pk):
        queryset = Profile.objects.all()
        profile = get_object_or_404(queryset, pk=pk)
        dives = Dive.objects.filter(diver=profile.user)
        s = DiveSerializer(dives, many=True)
        return Response(s.data)

    @detail_route(methods=['get'])
    def divesites(self, request, pk):
        queryset = Profile.objects.all()
        profile = get_object_or_404(queryset, pk=pk)
        divesites = Divesite.objects.filter(owner=profile.user)
        serializer = DivesiteSerializer(divesites, many=True)
        return Response(serializer.data)
