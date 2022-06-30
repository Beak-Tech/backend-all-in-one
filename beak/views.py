from django.shortcuts import render
# Create your views here.
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from beak.models import Place, User, OpeningHours
from beak.serializers import PlaceSerializer, OpeningHoursSerializer
import datetime
from beak.utils import Place_Utils
from beak.utils import check_time_availbility, request_save_open_times_of_places


@api_view(['GET'])
def get_places(request):
    """
    Return a list of places according to the query parameters.
    """
    data = request.data
    place = data['place']  # place = 'Los Angeles'
    place_utils = Place_Utils(place, key_words=[
                              'Golf', 'Escape game', 'Go Kart', 'Bowling', 'Archery', 'Shooting Range'])
    serializer = PlaceSerializer(data=place_utils.turn_to_model(), many=True)
    if serializer.is_valid():
        place_objects = serializer.save()
    for place in place_objects:
        request_save_open_times_of_places(place)
    check_time_availbility(data['start_time'], data['end_time'], )
