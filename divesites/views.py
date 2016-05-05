from actstream import action
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from haversine import haversine
from rest_framework import mixins
from rest_framework import viewsets
from rest_framework import status
from rest_framework.decorators import detail_route, list_route
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from .serializers import CompressorSerializer, DiveSerializer, DiveListSerializer,  DivesiteSerializer, DivesiteListSerializer, SlipwaySerializer
from .models import Compressor, Dive, Divesite, Slipway
from .permissions import IsDiverOrReadOnly, IsOwnerOrReadOnly
from comments.models import DivesiteComment, SlipwayComment, CompressorComment
from comments.serializers import DivesiteCommentSerializer, CompressorCommentSerializer, SlipwayCommentSerializer 
from images.models import Image
from images.serializers import ImageSerializer

class BaseSiteViewSet(viewsets.ModelViewSet):

    # The default permission classes are
    # (a) safe methods only if unauthenticated;
    # (b) safe methods only if not the owner of the site
    permission_classes = (IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly,)

    @detail_route(methods=['get', 'post', 'delete'])
    def header_image(self, request, pk):
        # Permissions here should be handled by the viewset's permission_classes

        site = self.get_object()

        if request.method == 'DELETE':
            # Find an image for this site that is currently flagged as a header
            # image, unflag it, and save
            try:
                image = site.images.get(is_header_image=True)
                image.is_header_image = False
                image.save()
            except Image.DoesNotExist:
                pass
            return Response({}, status=status.HTTP_204_NO_CONTENT)

        if request.method == 'GET':
            # Look for an image with is_header_image set to True, and return
            # it if it exists; otherwise, return an empty object and HTTP 204.
            try:
                image = site.images.get(is_header_image=True)
                serializer = ImageSerializer(image)
                return Response(serializer.data)
            except Image.DoesNotExist:
                # This is not a problem; we expect a call to get /header_image/
                # for every divesite. (In fact we expect them so frequently that
                # we should probably send it when we serialize a divesite.)
                return Response({}, status=status.HTTP_204_NO_CONTENT)

        if request.method == 'POST':
            site = self.get_object()
            # Look for the image associated with this site with the ID in
            # the post body and set it as the header image. The task of
            # ensuring that only one image is a header is performed at
            # the model level.
            try:
                image = site.images.get(id=request.data['id'])
                image.is_header_image = True
                image.save()
                # As a courtesy, return the serialized version of this
                # image to the caller
                serializer = ImageSerializer(image)
                return Response(serializer.data)
            except Image.DoesNotExist:
                # This is definitely a client error; you shouldn't be
                # trying to set an image that doesn't belong to this
                # site as its header.
                raise NotFound()


class DivesiteViewSet(BaseSiteViewSet):

    queryset = Divesite.objects.all()
    serializer_class = DivesiteSerializer

    def perform_create(self, serializer):
        # Get the user from the request
        user = self.request.user
        instance = serializer.save(owner=user)

    def list(self, request):
        queryset = self.get_queryset()
        serializer = DivesiteListSerializer(queryset, many=True)
        return Response(serializer.data)

    @detail_route(methods=['get'])
    def comments(self, request, pk):
        # Return comments on this divesite
        queryset = DivesiteComment.objects.filter(divesite=self.get_object())
        serializer = DivesiteCommentSerializer(queryset, many=True)
        return Response(serializer.data)

    @detail_route(methods=['get'])
    def dives(self, request, pk):
        # Return dives at this divesite
        divesite = self.get_object()
        queryset = Dive.objects.filter(divesite=divesite)
        # Use DiveListSerializer since we don't need more than a
        # MinimalProfileSerializer and a primary key for the divesite
        serializer = DiveListSerializer(queryset, many=True)
        return Response(serializer.data)


    @detail_route(methods=['get'])
    def nearby_slipways(self, request, pk):
        # Return nearby slipways for this divesite
        NEARBY_SLIPWAY_KM_LIMIT = 15
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
                    ) <= NEARBY_SLIPWAY_KM_LIMIT]
        serializer = SlipwaySerializer(slipways, many=True)
        return Response(serializer.data)


class DiveViewSet(viewsets.GenericViewSet,
        # Don't mix in ListModelMixin: we don't want an API endpoint for
        # it (there's no use-case for 'list all dives')
        mixins.CreateModelMixin,
        mixins.RetrieveModelMixin,
        mixins.UpdateModelMixin,
        mixins.DestroyModelMixin):

    permission_classes = (IsAuthenticatedOrReadOnly,IsDiverOrReadOnly,)
    queryset = Dive.objects.all()
    serializer_class = DiveSerializer

    def perform_create(self, serializer):
        # Get the divesite instance from the request
        divesite = Divesite.objects.get(id=self.request.data['divesite'])
        # Get the user from the request
        user = self.request.user
        # Unless we explicitly set the divesite ID here, we get an IntegrityError (?)
        instance = serializer.save(diver=user, divesite=divesite)


class CompressorViewSet(BaseSiteViewSet):
    queryset = Compressor.objects.all()
    serializer_class = CompressorSerializer

    def perform_create(self, serializer):
        # Get the user from the request
        owner = self.request.user
        # Save the instance
        instance = serializer.save(owner=owner)

    @detail_route(methods=['get'])
    def comments(self, request, pk):
        # Return comments on this compressor
        queryset = CompressorComment.objects.filter(compressor=self.get_object())
        serializer = CompressorCommentSerializer(queryset, many=True)
        return Response(serializer.data)


class SlipwayViewSet(BaseSiteViewSet):
    queryset = Slipway.objects.all()
    serializer_class = SlipwaySerializer

    def perform_create(self, serializer):
        # Get the user from the request
        owner = self.request.user
        # Save the instance
        instance = serializer.save(owner=owner)

    @detail_route(methods=['get'])
    def comments(self, request, pk):
        queryset = SlipwayComment.objects.filter(slipway=self.get_object())
        serializer = SlipwayCommentSerializer(queryset, many=True)
        return Response(serializer.data)
