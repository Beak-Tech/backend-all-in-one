from django.db import models

# Create your models here.
WEEKDAYS = [
    (0, "Monday"),
    (1, "Tuesday"),
    (2, "Wednesday"),
    (3, "Thursday"),
    (4, "Friday"),
    (5, "Saturday"),
    (6, "Sunday"),
]

# The model to implement cacheing for the recommendations:
# E.g: The first time we search berkeley, we will store every place in the General_Location(Berkeley)
#      and all future searches about berkeley will return the same results (unless different opening times).


class General_Location_for_Eat(models.Model):
    places = models.ManyToManyField('Place', blank=True)
    name = models.CharField(max_length=100, blank=False, primary_key=True)

    def __str__(self):
        return self.name


class General_Location_for_Play(models.Model):
    places = models.ManyToManyField('Place', blank=True)
    name = models.CharField(max_length=100, blank=False, primary_key=True)

    def __str__(self):
        return self.name


class Token(models.Model):
    number = models.CharField(max_length=64, blank=False, primary_key=True)
    play_places = models.ManyToManyField(
        'Place', blank=True, related_name='play_places')
    eat_places = models.ManyToManyField(
        'Place', blank=True, related_name='eat_places')


class Place(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=200, blank=False)
    google_id = models.CharField(max_length=200, blank=False, primary_key=True)
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
