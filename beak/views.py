import keyword
from django.shortcuts import render
# Create your views here.
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from beak.serializers import PlaceSerializer
from beak.utils import get_some_places_to_play_with_token, get_token_utils
from beak.utils import get_some_play, get_some_eat
from beak.models import Token, Place, User, OpeningHours, General_Location_for_Eat, General_Location_for_Play


@api_view(['POST'])
def get_places(request):
    print('POST get_places request received')
    data = request.data
    place = data['location']  # place = 'Los Angeles'
    valid_play, valid_eat = None, None
    if data['item'] == 0 or data['item'] == 2:
        valid_play = get_some_play(
            place, data['start'], data['end'], keywords=[
                'Golf', 'Escape game', 'Go Kart'])

    if data['item'] == 1 or data['item'] == 2:
        valid_eat = get_some_eat(
            place, data['start'], data['end'], keywords=[
                'Restaurant', 'Fast Food', 'Pizza'])
    ret = {'places': PlaceSerializer(
        valid_play, many=True).data, 'eat': PlaceSerializer(valid_eat, many=True).data}
    return Response(ret, status=status.HTTP_200_OK)


@api_view(['POST'])
def get_token(request):
    print('POST get_token request received')
    data = request.data
    place = data['location']
    # Item 0 means play, 1 means eat, 2 means both
    token = get_token_utils(place, data['start'], data['end'], keywords=[
        'Golf', 'Escape game', 'Go Kart'], play_or_eat=data['item'])
    return Response({"token": token}, status=status.HTTP_200_OK)


@api_view(['GET'])
def get_place_with_token(request):
    print('GET request received')
    data = request.data
    '''
Place.objects.all().delete()
OpeningHours.objects.all().delete()
General_Location_for_Eat.objects.all().delete()
General_Location_for_Play.objects.all().delete()
Token.objects.all().delete()
    '''
    num = data['token']
    valid_play, valid_eat = get_some_places_to_play_with_token(num)
    ret = {'places':  PlaceSerializer(
        valid_play, many=True).data, 'eat': PlaceSerializer(valid_eat, many=True).data}
    return Response(ret, status=status.HTTP_200_OK)


@api_view(['GET'])
def hello(request):
    return Response("Hello, world. You're at the Beak", status=status.HTTP_200_OK)
