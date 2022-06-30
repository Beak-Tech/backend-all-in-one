from django.shortcuts import render
from recsys.beak.utils import check_time_availbility

# Create your views here.
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from beak.models import Place, User
from beak.serializers import PlaceSerializer, OpeningHoursSerializer
import datetime
from beak.utils import Place_Utils


@api_view(['GET'])
def get_places(request):
    """
    Return a list of places according to the query parameters.
    """
    data = request.data
    place = data['place']
    place_utils = Place_Utils(place, key_words=[
                              'Golf', 'Escape game', 'Go Kart', 'Bowling', 'Archery', 'Shooting Range'])
    serializer = PlaceSerializer(place_utils.turn_to_model(), many=True)
    place_utils.request_open_times_of_places
    check_time_availbility(data['start_time'], data['end_time'], )
