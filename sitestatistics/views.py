from django.shortcuts import render
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response

from divesites.models import Compressor, Dive, Divesite, Slipway
from images.models import Image
from profiles.models import Profile

# Create your views here.
@api_view(['GET'])
@renderer_classes((JSONRenderer,))
def site_statistics(request):
    compressors = Compressor.objects.count()
    dives = Dive.objects.count()
    divesites = Divesite.objects.count()
    images = Image.objects.count()
    slipways = Slipway.objects.count()
    # Cache Machine doesn't play well with values_list
    # (see https://github.com/django-cache-machine/django-cache-machine/issues/116)
    # so we'll just ask for the full set of Dive objects and then iterate over them
    # rather than getting nothing but their duration
    total_hours_underwater = int(sum([dive.duration.seconds for dive in Dive.objects.all()]) / 3600)
    users = Profile.objects.count()
    obj = {
            'compressors': compressors,
            'dives': dives,
            'divesites': divesites,
            'images': images,
            'slipways': slipways,
            'total_hours_underwater': total_hours_underwater,
            'users': users,
            }
    return Response(obj)
