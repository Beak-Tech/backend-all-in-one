import keyword
from django.shortcuts import render
# Create your views here.
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
import json
from beak.serializers import PlaceSerializer
from beak.utils import get_some_places_to_play_with_token, get_token_utils, get_categories_for_token
from beak.utils import get_some_play, get_some_eat
from beak.models import Token, Place, User, OpeningHours, General_Location_for_Eat, General_Location_for_Play
from beak.place_keywords import in_door_activities, out_door_activities


@api_view(['POST'])
def get_places(request):
    print('POST get_places request received')
    data = request.data
    place = data['location']  # place = 'Los Angeles'
    valid_play, valid_eat = None, None
    if data['item'] == 0 or data['item'] == 2:
        valid_play = get_some_play(
            place, data['start'], data['end'], keywords=in_door_activities[:3])

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
    token = get_token_utils(place, data['start'], data['end'],
                            keywords=in_door_activities[:3], play_or_eat=data['item'])
    return Response({"token": token}, status=status.HTTP_200_OK)


@api_view(['GET'])
def get_place_with_token(request, token_num):
    print('GET request received')
    '''
Place.objects.all().delete()
OpeningHours.objects.all().delete()
General_Location_for_Eat.objects.all().delete()
General_Location_for_Play.objects.all().delete()
Token.objects.all().delete()
    '''
    if not token_num:
        return Response({"error": "No token number provided"}, status=status.HTTP_400_BAD_REQUEST)
    valid_play, valid_eat = get_some_places_to_play_with_token(token_num)
    ret = {'places':  PlaceSerializer(
        valid_play, many=True).data, 'eat': PlaceSerializer(valid_eat, many=True).data}
    return Response(ret, status=status.HTTP_200_OK)


@api_view(['GET'])
def get_category_with_token(request, token_num):
    if not token_num:
        return Response({"error": "No token number provided"}, status=status.HTTP_400_BAD_REQUEST)
    categories = get_categories_for_token(token_num)
    print(categories)
    return Response(json.loads(categories), status=status.HTTP_200_OK)


@api_view(['GET'])
def hello(request):
    return Response("Hello, world. You're at the Beak", status=status.HTTP_200_OK)
