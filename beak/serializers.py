from rest_framework import serializers
from beak.models import Category, Place, User, OpeningHours, Token


class PlaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Place
        fields = ['name', 'address', 'google_id',
                  'google_rating', 'website', 'image_url', 'category_name']


class OpeningHoursSerializer(serializers.ModelSerializer):
    class Meta:
        model = OpeningHours
        fields = ['weekday', 'from_hour', 'to_hour', 'place']


class TokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Token
        fields = ['number', 'places']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['name', 'places']
   

# a= datetime.time.now()
#p = Place(name="ok", address="ok_address", google_id = 'example_id', google_rating = 3.4)
#oph = OpeningHours(place = p, weekday = 0, from_hour =a, to_hour = a)
# a= datetime.time.now()
#p = Place(name="ok", address="ok_address", google_id = 'example_id', google_rating = 3.4)
#oph = OpeningHours(place = p, weekday = 0, from_hour =a, to_hour = a)
