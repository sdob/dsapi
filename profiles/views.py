from actstream.actions import follow, unfollow
from actstream.models import Action, followers, following, user_stream
from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404
from rest_framework import exceptions
from rest_framework import mixins
from rest_framework import pagination
from rest_framework import permissions
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import api_view, detail_route, list_route, permission_classes
from rest_framework.exceptions import NotAuthenticated, PermissionDenied
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from .models import Profile
from .permissions import IsProfileOwnerOrReadOnly
from .serializers import MinimalProfileSerializer, OwnProfileSerializer, ProfileSerializer, ActionSerializer
from divesites.models import Dive, Divesite
from divesites.serializers import DiveSerializer, DiveListSerializer, DivesiteSerializer
from images.models import Image, UserProfileImage
from images.serializers import ImageSerializer, UserProfileImageSerializer


class FeedPaginator(pagination.LimitOffsetPagination):
    default_limit = 10


class ProfileViewSet(viewsets.GenericViewSet,
        mixins.UpdateModelMixin,
        mixins.RetrieveModelMixin):

    permission_classes = (IsAuthenticatedOrReadOnly, IsProfileOwnerOrReadOnly)
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer

    @detail_route(methods=['post'], permission_classes=[IsAuthenticated])
    def follow(self, request, pk):
        # You can't follow yourself. We have to cast the UUID to a string
        # (since 'blah' != UUID('blah').
        if pk == str(request.user.profile.id):
            raise exceptions.PermissionDenied(detail="You cannot follow yourself")
        queryset = Profile.objects.all()
        profile = get_object_or_404(queryset, pk=pk)
        user = profile.user
        # Now get django-activity-stream to follow
        data = follow(request.user, user)
        # TODO: Return something informative to the client
        return Response({}, status=status.HTTP_200_OK, content_type='json')

    @detail_route(methods=['get'])
    def followers(self, request, pk):
        queryset = Profile.objects.all()
        profile = get_object_or_404(queryset, pk=pk)
        user = profile.user
        targets = followers(user)
        profiles = [_.profile for _ in targets]
        serializer = ProfileSerializer(profiles, many=True)
        return Response(serializer.data)

    @detail_route(methods=['get'])
    def follows(self, request, pk):
        queryset = Profile.objects.all()
        profile = get_object_or_404(queryset, pk=pk)
        user = profile.user
        targets = following(user)
        profiles = [_.profile for _ in targets]
        serializer = ProfileSerializer(profiles, many=True)
        return Response(serializer.data)

    @detail_route(methods=['post'], permission_classes=[IsAuthenticated])
    def unfollow(self, request, pk):
        # You can't unfollow yourself
        if pk == str(request.user.profile.id):
            raise exceptions.PermissionDenied(detail="You cannot unfollow yourself")
        queryset = Profile.objects.all()
        profile = get_object_or_404(queryset, pk=pk)
        user = profile.user
        # Now get django-activity-stream to follow
        data = unfollow(request.user, user)
        # TODO: Return something informative to the client
        return Response({}, status=status.HTTP_200_OK, content_type='json')

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
        qs = user_stream(user, with_user_activity=True)
        # Paginate the queryset
        paginator = FeedPaginator()
        paginated_queryset = paginator.paginate_queryset(qs, request, view=self)
        serializer = ActionSerializer(paginated_queryset, many=True)
        # Generate a response
        paginated_response = paginator.get_paginated_response(serializer.data)
        return paginated_response

    @list_route(methods=['get'], permission_classes=[IsAuthenticated])
    def my_followers(self, request):
        user = request.user
        targets = followers(user)
        target_profiles = [_.profile for _ in targets]
        serializer = ProfileSerializer(target_profiles, many=True)
        return Response(serializer.data)

    @list_route(methods=['get'], permission_classes=[IsAuthenticated])
    def my_follows(self, request):
        user = request.user
        targets = following(user, User)
        target_profiles = [_.profile for _ in targets]
        serializer = ProfileSerializer(target_profiles, many=True)
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
    def images(self, request, pk):
        profile = get_object_or_404(Profile.objects.all(), pk=pk)
        images = Image.objects.filter(owner=profile.user).order_by('-creation_date')
        serializer = ImageSerializer(images, many=True)
        return Response(serializer.data)


    @detail_route(methods=['get'])
    def minimal(self, request, pk):
        # Just get user name and ID
        profile = get_object_or_404(Profile.objects.all(), pk=pk)
        serializer = MinimalProfileSerializer(profile)
        return Response(serializer.data)

    @detail_route(methods=['get', 'post', 'delete'], permission_classes=[IsAuthenticatedOrReadOnly],)
    def profile_image(self, request, pk):
        if not request.method in permissions.SAFE_METHODS:
            if not request.user.is_authenticated():
                raise NotAuthenticated()
            if not str(request.user.profile.id) == pk:
                raise PermissionDenied()

        profile = get_object_or_404(Profile.objects.all(), pk=pk)

        if request.method == 'GET':
            try:
                image = UserProfileImage.objects.get(user__profile=profile)
                serializer = UserProfileImageSerializer(image)
                return Response(serializer.data)
            except UserProfileImage.DoesNotExist:
                return Response({}, status=status.HTTP_204_NO_CONTENT, content_type='json')

        if request.method == 'POST':
            # Delete any existing profile image
            try:
                UserProfileImage.objects.get(user=profile.user).delete()
            except UserProfileImage.DoesNotExist:
                pass
            # Create a new one
            UserProfileImage.objects.create(user=profile.user, image=request.data['image'])
            image = UserProfileImage.objects.get(user__profile=profile)
            serializer = UserProfileImageSerializer(image)
            return Response(serializer.data)

        if request.method == 'DELETE':
            UserProfileImage.objects.filter(user__profile=profile).delete()
            return Response({}, status=status.HTTP_204_NO_CONTENT, content_type='json')
