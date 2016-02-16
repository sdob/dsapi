from actstream.models import Action, user_stream
from django.shortcuts import render, get_object_or_404
from rest_framework import mixins
from rest_framework import pagination
from rest_framework import viewsets
from rest_framework.decorators import api_view, detail_route, list_route, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from .models import Profile
from .permissions import IsProfileOwnerOrReadOnly
from .serializers import MinimalProfileSerializer, OwnProfileSerializer, ProfileSerializer, ActionSerializer
from divesites.models import Dive, Divesite
from divesites.serializers import DiveSerializer, DiveListSerializer, DivesiteSerializer


class FeedPaginator(pagination.LimitOffsetPagination):
    default_limit = 10


class ProfileViewSet(viewsets.GenericViewSet,
        mixins.UpdateModelMixin,
        mixins.RetrieveModelMixin):

    permission_classes = (IsAuthenticatedOrReadOnly, IsProfileOwnerOrReadOnly)
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer

    @list_route(methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        """Return the requesting user's own profile."""
        serializer = OwnProfileSerializer(request.user.profile)
        return Response(serializer.data)

    @list_route(methods=['get'], permission_classes=[IsAuthenticated])
    def my_feed(self, request):
        """
        Retrieve the list of actions for which the requesting user is
        (a) the actor
        """
        user = request.user
        stream = Action.objects.all()
        qs = stream.filter(actor_object_id=user.id)
        # Paginate the queryset
        paginator = FeedPaginator()
        paginated_queryset = paginator.paginate_queryset(qs, request, view=self)
        serializer = ActionSerializer(paginated_queryset, many=True)
        # Generate a response
        paginated_response = paginator.get_paginated_response(serializer.data)
        return paginated_response

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
    def feed(self, request, pk):
        queryset = Profile.objects.all()
        profile = get_object_or_404(queryset, pk=pk)
        qs = Action.objects.filter(actor_object_id=profile.user.id)
        # Paginate the queryset
        paginator = FeedPaginator()
        paginated_queryset = paginator.paginate_queryset(qs, request, view=self)
        serializer = ActionSerializer(paginated_queryset, many=True)
        # Generate a response
        paginated_response = paginator.get_paginated_response(serializer.data)
        return paginated_response

    @detail_route(methods=['get'])
    def minimal(self, request, pk):
        # Just get user name and ID
        profile = get_object_or_404(Profile.objects.all(), pk=pk)
        serializer = MinimalProfileSerializer(profile)
        return Response(serializer.data)
