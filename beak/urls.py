from django.urls import path
from beak.views import get_places, hello

urlpatterns = [
    path('places/', get_places),
    path('', hello)
]
