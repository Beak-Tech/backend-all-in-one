from rest_framework import serializers
from beak.models import Place, User, OpeningHours, Token


class PlaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Place
        fields = ['name', 'address', 'google_id',
                  'google_rating', 'website', 'image_url', 'category']


class OpeningHoursSerializer(serializers.ModelSerializer):
    class Meta:
        model = OpeningHours
        fields = ['weekday', 'from_hour', 'to_hour', 'place']


class TokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Token
        fields = ['number', 'play_places', 'eat_places',
                  'categories']
