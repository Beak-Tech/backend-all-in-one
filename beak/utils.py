import requests
import json
import collections
import datetime
from beak.serializers import PlaceSerializer, OpeningHoursSerializer
from beak.models import Place, OpeningHours


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
        api_url = 'https://maps.googleapis.com/maps/api/place/textsearch/json?query={}&key={}' \
            .format(key_word, self.api_key)
        response = requests.get(api_url)
        json_response = json.loads(response.text)
        self.results[key_word] = json_response['results']

    def result_filter(self, results):
        place_ids = []
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
                if 'address' not in self.places[place_id] or 'name' not in self.places[place_id] or self.places[place_id]['google_rating'] < 3.0:
                    self.places.pop(place_id)
                else:
                    place_ids.append(place_id)
                continue
            place_ids.append(place_id)
        arrival_times, arrival_times_text, distances, distances_text = self.get_arrival_time_distances(
            place_ids)
        for place_id, at, attext, dis, distext in zip(place_ids, arrival_times, arrival_times_text, distances, distances_text):
            self.places[place_id]['arrival_time'] = at
            self.places[place_id]['arrival_time_text'] = attext
            self.places[place_id]['distance'] = dis
            self.places[place_id]['distance_text'] = distext

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
    start_weekday = start_datetime.weekday()
    end_weekday = end_datetime.weekday()
    start_weekday_opening_hours = OpeningHoursSerializer(
        opening_hours.filter(weekday=start_weekday), many=True).data[0]
    end_weekday_opening_hours = OpeningHoursSerializer(
        opening_hours.filter(weekday=end_weekday), many=True).data[0]
    start_weekday_open_time = datetime.datetime.strptime(
        start_weekday_opening_hours['from_hour'], '%H:%M:%S').time()
    end_weekday_close_time = datetime.datetime.strptime(
        end_weekday_opening_hours['to_hour'], '%H:%M:%S').time()
    if start_weekday_open_time > start_datetime.time() or end_weekday_close_time < end_datetime.time():
        return False
    return True


def request_save_open_times_of_places(place, api_key='AIzaSyD80xO_hx4nYwmRCVBL_uotZHm1udWDwRs'):
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
            continue

        def google_weekday_to_datetime_weekday(x):
            return x - 1 if x > 0 else 6
        curr_weekday_hours = OpeningHours(
            place=place, weekday=google_weekday_to_datetime_weekday(
                wwekday),
            from_hour=datetime.time(int(open_time[:2]), int(open_time[2:])),
            to_hour=datetime.time(int(close_time[:2]), int(close_time[2:])))
        curr_weekday_hours.save()
    return True
