import keyword
import requests
import json
import collections
import datetime
from beak.serializers import PlaceSerializer, OpeningHoursSerializer
from beak.models import Place, OpeningHours, General_Location


class Place_Utils:
    def __init__(self, origin, key_words=[], api_key='AIzaSyD80xO_hx4nYwmRCVBL_uotZHm1udWDwRs', results={}):
        self.key_words = key_words
        self.origin = origin
        self.api_key = api_key
        self.results = results
        self.places = collections.defaultdict(dict)
        for key_word in key_words:
            self.text_search(key_word)
        for key_word, results in self.results.items():
            self.result_filter(results)

    def text_search(self, key_word):
        # Places API
        api_url = 'https://maps.googleapis.com/maps/api/place/textsearch/json?query={} in {}&key={}' \
            .format(key_word, self.origin, self.api_key)
        response = requests.get(api_url)
        json_response = json.loads(response.text)
        self.results[key_word] = json_response['results']

    def result_filter(self, results):
        for result in results:
            try:
                if result['business_status'] != 'OPERATIONAL':
                    continue
                place_id = result['place_id']
                self.places[place_id]['name'] = result['name']
                self.places[place_id]['open_now'] = result['opening_hours']['open_now']
                self.places[place_id]['address'] = result['formatted_address']
                self.places[place_id]['google_rating'] = result['rating']
                self.places[place_id]['types'] = result['types']
            except KeyError:
                if 'address' not in self.places[place_id] or 'name' not in self.places[place_id] \
                        or 'google_rating' not in self.places[place_id] \
                        or self.places[place_id]['google_rating'] < 3.0:
                    self.places.pop(place_id)

    def get_arrival_time_distances(self, place_ids):
        dests = ['place_id:{}|'.format(place_id) for place_id in place_ids]
        dest_text = ''.join(dests)
        # Distance Matrix API
        api_url = 'https://maps.googleapis.com/maps/api/distancematrix/json?destinations={}&origins={}&key={}' \
            .format(dest_text, self.origin, self.api_key)
        response = requests.get(api_url)
        json_response = json.loads(response.text)
        arrival_times = []
        arrival_times_text = []
        distances = []
        distances_text = []
        for driving_status in json_response['rows'][0]['elements']:
            arrival_times_text.append(driving_status['duration']['text'])
            arrival_times.append(driving_status['duration']['value'])
            distances.append(driving_status['distance']['value'])
            distances_text.append(driving_status['distance']['text'])
        return arrival_times, arrival_times_text, distances, distances_text

    def sort_places_by_distance(self):
        sorted_places = sorted(self.places.items(),
                               key=lambda x: x[1]['distance'])
        return sorted_places

    def get_open_now_places(self):
        open_now_places = []
        for place_id, place in self.places.items():
            if place['open_now']:
                open_now_places.append(place_id)
        return open_now_places

    def turn_to_model(self):
        ret = []
        for googleid, info in self.places.items():
            if Place.objects.filter(google_id=googleid).exists():
                continue
            cur_dic = {}
            cur_dic['google_id'] = googleid
            cur_dic['name'] = info['name']
            cur_dic['address'] = info['address']
            cur_dic['google_rating'] = info['google_rating']
            ret.append(cur_dic)
        return ret

# The logic remains to be updated.


def check_time_availbility(start_str, end_str, opening_hours):
    start_datetime = datetime.datetime.strptime(
        start_str, '%Y-%m-%dT%H:%M')
    end_datetime = datetime.datetime.strptime(
        end_str, '%Y-%m-%dT%H:%M')
    time_dif = end_datetime - start_datetime
    if time_dif > datetime.timedelta(hours=168):
        return True
    start_weekday = start_datetime.weekday()
    end_weekday = end_datetime.weekday()
    # This is in case we start at Friday and end at Monday, which will prevent the for loop from running.
    if start_weekday > end_weekday:
        end_weekday += 7
    # As long as the days between start and end have any opening hour, we can return True.
    for weekday in range(start_weekday + 1, end_weekday):
        # In case we might add 7 to end_weekday, we need to mod 7 to get the correct weekday.
        actual_day = weekday % 7
        weekday_opening_hours = OpeningHoursSerializer(
            opening_hours.filter(weekday=actual_day), many=True).data[0]
        weekday_open_time = datetime.datetime.strptime(
            weekday_opening_hours['from_hour'], '%H:%M:%S').time()
        weekday_close_time = datetime.datetime.strptime(
            weekday_opening_hours['to_hour'], '%H:%M:%S').time()
        if weekday_open_time != weekday_close_time:
            return True
    # We will need to check the start day then.
    startday_opening_hours = OpeningHoursSerializer(
        opening_hours.filter(weekday=start_weekday), many=True).data[0]
    startday_close_time = datetime.datetime.strptime(
        startday_opening_hours['from_hour'], '%H:%M:%S').time()
    if startday_close_time > start_datetime.time():
        return True
    endday_opening_hours = OpeningHoursSerializer(
        opening_hours.filter(weekday=end_weekday), many=True).data[0]
    endday_open_time = datetime.datetime.strptime(
        endday_opening_hours['to_hour'], '%H:%M:%S').time()
    if endday_open_time < end_datetime.time():
        return True
    return False


def request_save_open_times_of_places(place, api_key='AIzaSyD80xO_hx4nYwmRCVBL_uotZHm1udWDwRs'):
    # Return early if the opening hours are already saved.
    if OpeningHours.objects.filter(place=place).exists():
        return True
    # Place API : Place Details https://developers.google.com/maps/documentation/places/web-service/details#required-parameters
    api_url = 'https://maps.googleapis.com/maps/api/place/details/json?place_id={}&key={}&fields=opening_hours/periods' \
        .format(place.google_id, api_key)
    response = requests.get(api_url)
    json_response = json.loads(response.text)
    for period in json_response['result']['opening_hours']['periods']:
        try:
            open_time = period['open']['time']
            close_time = period['close']['time']
            wwekday = period['open']['day']
        except KeyError:
            print('KeyError: {}'.format(place.google_id))
            return False

        def google_weekday_to_datetime_weekday(x):
            return x - 1 if x > 0 else 6
        if OpeningHours.objects.filter(place=place, weekday=google_weekday_to_datetime_weekday(wwekday)).exists():
            print('Duplicate: {}'.format(place.google_id))
            return False
        curr_weekday_hours = OpeningHours(
            place=place, weekday=google_weekday_to_datetime_weekday(
                wwekday),
            from_hour=datetime.time(int(open_time[:2]), int(open_time[2:])),
            to_hour=datetime.time(int(close_time[:2]), int(close_time[2:])))
        curr_weekday_hours.save()
    return True


def get_some_places_to_play(place, start_date, end_date, keywords):
    if General_Location.objects.filter(name=place).exists():
        valid_places = General_Location.objects.get(name=place).places.all()
    else:
        new_loc = General_Location(name=place)
        new_loc.save()
        place_utils = Place_Utils(place, key_words=keywords)
        serializer = PlaceSerializer(
            data=place_utils.turn_to_model(), many=True)
        if serializer.is_valid():
            place_objects = serializer.save()
        valid_places = []
        print('retrieved places, now filtering')
        for place in place_objects:
            if not request_save_open_times_of_places(place):
                # The place has a wrongly formatted opening times, so just delete the place.
                place.delete()
                continue
            new_loc.places.add(place)
            valid_places.append(place)
            # We save the place in General_Location for cache:
    time_match_places = []
    for valid_place in valid_places:
        if check_time_availbility(
                start_date, end_date, OpeningHours.objects.filter(place=valid_place)):
            time_match_places.append(valid_place)
    return PlaceSerializer(time_match_places, many=True).data
