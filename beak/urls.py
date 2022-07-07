from django.urls import path
from beak.views import get_places

urlpatterns = [
    path('places/', get_places),
]
