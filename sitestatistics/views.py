from django.shortcuts import render
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response

from divesites.models import Compressor, Dive, Divesite, Slipway
from profiles.models import Profile

# Create your views here.
@api_view(['GET'])
@renderer_classes((JSONRenderer,))
def site_statistics(request):
    compressors = Compressor.objects.count()
    dives = Dive.objects.count()
    divesites = Divesite.objects.count()
    users = Profile.objects.count()
    obj = {
            'compressors': compressors,
            'dives': dives,
            'divesites': divesites,
            'users': users
            }
    return Response(obj)
