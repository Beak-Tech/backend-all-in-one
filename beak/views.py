import keyword
from django.shortcuts import render
# Create your views here.
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from beak.models import Place, User, OpeningHours, Token
from beak.serializers import PlaceSerializer, OpeningHoursSerializer
import datetime
from beak.utils import Place_Utils, get_some_places_to_play_with_token, get_token_utils
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
    place = data['place']  # place = 'Los Angeles'
    if data['event']['play']:
        valid_play = get_some_places_to_play(
            place, data['start_time'], data['end_time'], keywords=[
                'Golf', 'Escape game', 'Go Kart'])
    """
    if data['event']['eat']:
        valid_eat = get_some_places_to_play(
            place, data['start_time'], data['end_time'], keywords=[
                'Restaurant', 'Fast Food', 'Pizza'])
    """
    ret = {'places': valid_play, 'eat': {}}
    return Response(ret, status=status.HTTP_200_OK)


@api_view(['GET'])
def get_token(request):
    print('GET request received')
    data = request.data
    '''
Place.objects.all().delete()
OpeningHours.objects.all().delete()
General_Location.objects.all().delete()
Token.objects.all().delete()
    '''
    place = data['place']
    token = get_token_utils(place, data['start_time'], data['end_time'], keywords=[
        'Golf', 'Escape game', 'Go Kart'])
    return Response({"token": token}, status=status.HTTP_200_OK)


@api_view(['GET'])
def get_place_with_token(request):
    print('GET request received')
    data = request.data
    '''
Place.objects.all().delete()
OpeningHours.objects.all().delete()
General_Location.objects.all().delete()
Token.objects.all().delete()
    '''
    num = data['token']  # place = 'Los Angeles'
    if data['event']['play']:
        valid_play = get_some_places_to_play_with_token(num)
    """
    if data['event']['eat']:
        valid_eat = get_some_places_to_play(
            place, data['start_time'], data['end_time'], keywords=[
                'Restaurant', 'Fast Food', 'Pizza'])
    """
    ret = {'places': valid_play, 'eat': {}}

    return Response(ret, status=status.HTTP_200_OK)
