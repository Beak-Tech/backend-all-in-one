from django.shortcuts import render

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
    planned_times = data['planned_times']
