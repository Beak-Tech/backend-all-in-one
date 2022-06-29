from django.db import models

# Create your models here.
WEEKDAYS = [
    (1, "Monday"),
    (2, "Tuesday"),
    (3, "Wednesday"),
    (4, "Thursday"),
    (5, "Friday"),
    (6, "Saturday"),
    (0, "Sunday"),
]


class Place(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=200, blank=False)
    google_id = models.CharField(max_length=100, blank=False, primary_key=True)
    google_rating = models.FloatField(default=-1)
    #business_status = models.CharField(max_length=100, blank=False)


class User(models.Model):
    name = models.CharField(max_length=100)
    recommended_places = models.ManyToManyField(Place)


class OpeningHours(models.Model):
    place = models.ForeignKey(
        Place,
        on_delete=models.CASCADE
    )
    weekday = models.IntegerField(
        choices=WEEKDAYS
    )
    from_hour = models.TimeField()
    to_hour = models.TimeField()

    class Meta:
        unique_together = ('place', 'weekday')
