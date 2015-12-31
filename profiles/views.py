from django.shortcuts import render, get_object_or_404
from rest_framework import mixins
from rest_framework import viewsets
from rest_framework.decorators import api_view, detail_route, list_route, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from .models import Profile
from .permissions import IsProfileOwnerOrReadOnly
from .serializers import ProfileSerializer
from divesites.models import Dive, Divesite
from divesites.serializers import DiveSerializer, DivesiteSerializer
from activity.models import Activity
import activity.serializers


class ProfileViewSet(viewsets.GenericViewSet,
        mixins.UpdateModelMixin,
        mixins.RetrieveModelMixin):

    permission_classes = (IsAuthenticatedOrReadOnly, IsProfileOwnerOrReadOnly)
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer

    @list_route(methods=['get'], permission_classes=[IsAuthenticated])
    #@list_route(methods=['get'])
    def me(self, request):
        print dir(request)
        print request.user.profile
        serializer = ProfileSerializer(request.user.profile)
        return Response(serializer.data)

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

    @detail_route(methods=['get'])
    def recent_activity(self, request, pk):
        # set an arbitrary upper level
        queryset = Profile.objects.all()
        max_items = 10
        profile = get_object_or_404(queryset, pk=pk)
        activities = Activity.objects.filter(user=profile.user).order_by('-creation_date').select_subclasses()[:max_items]
        data = [activity.serializers.serializer_factory(_)(_).data for _ in activities]
        return Response(data)
