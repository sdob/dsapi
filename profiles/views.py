from django.shortcuts import render, get_object_or_404
from rest_framework import mixins
from rest_framework import viewsets
from rest_framework.decorators import api_view, detail_route, list_route, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from .models import Profile
from .permissions import IsProfileOwnerOrReadOnly
from .serializers import MinimalProfileSerializer, OwnProfileSerializer, ProfileSerializer
from divesites.models import Dive, Divesite
from divesites.serializers import DiveSerializer, DiveListSerializer, DivesiteSerializer


class ProfileViewSet(viewsets.GenericViewSet,
        mixins.UpdateModelMixin,
        mixins.RetrieveModelMixin):

    permission_classes = (IsAuthenticatedOrReadOnly, IsProfileOwnerOrReadOnly)
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer

    @list_route(methods=['get'], permission_classes=[IsAuthenticated])
    #@list_route(methods=['get'])
    def me(self, request):
        serializer = OwnProfileSerializer(request.user.profile)
        return Response(serializer.data)

    @detail_route(methods=['get'])
    def dives(self, request, pk):
        queryset = Profile.objects.all()
        profile = get_object_or_404(queryset, pk=pk)
        dives = Dive.objects.filter(diver=profile.user)
        s = DiveListSerializer(dives, many=True)
        return Response(s.data)

    @detail_route(methods=['get'])
    def divesites(self, request, pk):
        queryset = Profile.objects.all()
        profile = get_object_or_404(queryset, pk=pk)
        divesites = Divesite.objects.filter(owner=profile.user)
        serializer = DivesiteSerializer(divesites, many=True)
        return Response(serializer.data)

    @detail_route(methods=['get'])
    def minimal(self, request, pk):
        # Just get user name and ID
        profile = get_object_or_404(Profile.objects.all(), pk=pk)
        serializer = MinimalProfileSerializer(profile)
        return Response(serializer.data)
