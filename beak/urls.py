from django.urls import path
from beak.views import get_places, get_token, get_place_with_token

urlpatterns = [
    path('places/', get_places),
    path('gettoken/', get_token),
    path('getplacewithtoken/', get_place_with_token),
]