from django.db import models

# Create your models here.


class Place(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=200, blank=False)
    google_id = models.CharField(max_length=100, blank=False, primary_key=True)
    google_rating = models.FloatField(default=-1)


class User(models.Model):
    name = models.CharField(max_length=100)
    recommended_places = models.ManyToManyField(Place)
