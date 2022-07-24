import keyword
from django.shortcuts import render
# Create your views here.
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from beak.models import Place, User, OpeningHours
from beak.serializers import PlaceSerializer, OpeningHoursSerializer
import datetime
from beak.utils import Place_Utils
from beak.utils import check_time_availbility, request_save_open_times_of_places, get_some_places_to_play


@api_view(['GET'])
def get_places(request):
    """
    Return a list of places according to the query parameters.
    """
    print('GET request received')
    data = request.data
    '''
Place.objects.all().delete()
OpeningHours.objects.all().delete()
General_Location.objects.all().delete()
    '''
    place = data['location']  # place = 'Los Angeles'
    valid_play, valid_eat = None, None
    if data['item'] == 0 or data['item'] == 2:
        valid_play = get_some_places_to_play(
            place, data['start'], data['end'], keywords=[
                'Golf', 'Escape game', 'Go Kart'])

    if data['item'] == 1 or data['item'] == 2:
        valid_eat = get_some_places_to_play(
            place, data['start'], data['end'], keywords=[
                'Restaurant', 'Fast Food', 'Pizza'])
    ret = {'places': valid_play, 'eat': {valid_eat}}
    return Response(ret, status=status.HTTP_200_OK)


@api_view(['GET'])
def hello(request):
    return Response("Hello, world. You're at the Beak", status=status.HTTP_200_OK)
