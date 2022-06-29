from django.db import models

# Create your models here.
WEEKDAYS = [
    (1, _("Monday")),
    (2, _("Tuesday")),
    (3, _("Wednesday")),
    (4, _("Thursday")),
    (5, _("Friday")),
    (6, _("Saturday")),
    (0, _("Sunday")),
]


class Place(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=200, blank=False)
    google_id = models.CharField(max_length=100, blank=False, primary_key=True)
    google_rating = models.FloatField(default=-1)
    #business_status = models.CharField(max_length=100, blank=False)
    open_hours = models.CharField(max_length=100, blank=False)


class User(models.Model):
    name = models.CharField(max_length=100)
    recommended_places = models.ManyToManyField(Place)


class OpeningHours(models.Model):
    store = models.ForeignKey(
        Place
    )
    weekday = models.IntegerField(
        choices=WEEKDAYS,
        unique_together=['store', 'weekday']
    )
    from_hour = models.TimeField()
    to_hour = models.TimeField()
