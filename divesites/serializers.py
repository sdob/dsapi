from rest_framework import serializers
from . import models

class DivesiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Divesite
