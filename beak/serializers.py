from rest_framework import serializers
from beak.models import Place, User


class PlaceSerializer(serializers.Serializer):
    class Meta:
        model = Place
        fields = ['name', 'address', 'google_id',
                  'google_rating', 'business_status', 'open_hours']
