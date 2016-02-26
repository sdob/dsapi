from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponseBadRequest
from django.shortcuts import render
from rest_framework import mixins, status, viewsets
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from divesites.models import Compressor, Divesite, Slipway
from divesites.permissions import IsOwnerOrReadOnly
from .models import Image
from .serializers import ImageSerializer

class ImageViewSet(viewsets.ModelViewSet):
    parser_classes = (FormParser, MultiPartParser,)
    permission_classes = (IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly,)
    queryset = Image.objects.all()
    serializer_class = ImageSerializer

    def check_ownership(self, obj):
        if 'is_header_image' in request.data:
            user = self.request.user


    def create(self, request, *args, **kwargs):
        if 'compressor_pk' in kwargs:
            obj = Compressor.objects.get(id=kwargs['compressor_pk'])
        elif 'divesite_pk' in kwargs:
            obj = Divesite.objects.get(id=kwargs['divesite_pk'])
        elif 'slipway_pk' in kwargs:
            obj = Slipway.objects.get(id=kwargs['slipway_pk'])
        if not obj:
            raise NotFound()
        # Add this in when everything else is functioning OK
        #self.check_ownership(obj)
        # Add to request
        print(request.data['image'])
        data = dict(request.data)
        data['content_type'] = ContentType.objects.get_for_model(obj).id
        data['object_id'] = obj.id
        image = Image.objects.create(
                content_object=obj,
                content_type=ContentType.objects.get_for_model(obj),
                image = request.data['image'],
                object_id = obj.id,
                owner=self.request.user,
                )
        print(image)
        serializer = ImageSerializer(image)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


    # Here's where it gets messy w.r.t. divesites/slipways/compressor
    def list(self, request, divesite_pk=None, slipway_pk=None, compressor_pk=None):
        images = Image.objects.none()
        if compressor_pk is not None:
            print('looking for images for compressor with pk: %s' % compressor_pk)
            obj = Compressor.objects.get(id=compressor_pk)
            images = obj.images.all()
        elif divesite_pk is not None:
            print('looking for images for divesite with pk: %s' % divesite_pk)
            obj = Divesite.objects.get(id=divesite_pk)
            images = obj.images.all()
        elif slipway_pk is not None:
            print('looking for images for slipway with pk: %s' % slipway_pk)
            obj = Slipway.objects.get(id=slipway_pk)
        if obj:
            images = obj.images.all()
        serializer = self.get_serializer(images, many=True)
        return Response(serializer.data)


    # TODO: check ownership of associated item before setting this as
    # the header image
    # def check_compressor_ownership(self, compressor):
        # user = self.request.user
        # if 'is_header_image' in self.request.data and not user == compressor.owner:
            # raise PermissionDenied()

    def perform_create(self, serializer):
        # Set the owner as the requesting user
        owner = self.request.user
        # Save the instance
        instance = serializer.save(owner=owner)

    def perform_update(self, serializer):
        # TODO: make this generic
        # compressor = Compressor.objects.get(id=self.request.data['compressor'])
        # TODO: Check site ownership
        # self.check_compressor_ownership(compressor)
        serializer.save()
