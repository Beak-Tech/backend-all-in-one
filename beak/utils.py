from hashlib import sha256
import random
import keyword
import requests
import json
import collections
import datetime
from beak.serializers import PlaceSerializer, OpeningHoursSerializer, TokenSerializer
from beak.models import Place, OpeningHours, General_Location_for_Eat, General_Location_for_Play, Token
from beak.place_keywords import in_door_activities, out_door_activities


class Place_Utils:
    def __init__(self, origin, key_words=None, api_key='AIzaSyD80xO_hx4nYwmRCVBL_uotZHm1udWDwRs', results={}):
        if key_words is None:
            key_words = []
        self.key_words = key_words
        self.origin = origin
        self.api_key = api_key
        self.results = results
        self.places = collections.defaultdict(dict)
        for key_word in key_words:
            self.text_search(key_word)
        for key_word, results in self.results.items():
            self.result_filter(results, key_word)

    def text_search(self, key_word):
        # Places API
        api_url = 'https://maps.googleapis.com/maps/api/place/textsearch/json?query={} in {}&key={}' \
            .format(key_word, self.origin, self.api_key)
        response = requests.get(api_url)
        json_response = json.loads(response.text)
        self.results[key_word] = json_response['results']

    def result_filter(self, results, category):
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
                self.places[place_id]['category'] = category
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
            cur_dic['category'] = info['category']
            ret.append(cur_dic)
        return ret

# The logic remains to be updated.


def check_time_availbility(start_str, end_str, opening_hours, google_id):
    start_datetime = datetime.datetime.strptime(
        start_str, '%Y-%m-%dT%H:%M')
    end_datetime = datetime.datetime.strptime(
        end_str, '%Y-%m-%dT%H:%M')
    time_dif = end_datetime - start_datetime
    if time_dif >= datetime.timedelta(hours=168):
        return True
    start_weekday = start_datetime.weekday()
    end_weekday = end_datetime.weekday()
    # This is in case we start at Friday and end at Monday, which will prevent the for loop from running.
    if start_weekday >= end_weekday:
        end_weekday += 7
    # As long as the days between start and end have any opening hour, we can return True.
    for weekday in range(start_weekday + 1, end_weekday):
        # In case we might add 7 to end_weekday, we need to mod 7 to get the correct weekday.
        actual_day = weekday % 7
        weekday_opening_hours = list(
            opening_hours.filter(weekday=actual_day))
        if not weekday_opening_hours:
            continue
        weekday_opening_hours = weekday_opening_hours[0]
        if weekday_opening_hours.from_hour != weekday_opening_hours.to_hour:
            return True
    # We will need to check the start day then.
    startday_opening_hours = list(opening_hours.filter(weekday=start_weekday))
    if startday_opening_hours:
        startday_opening_hours = startday_opening_hours[0]
        if startday_opening_hours.from_hour > start_datetime.time() > startday_opening_hours.to_hour:
            return True
    endday_opening_hours = list(opening_hours.filter(weekday=end_weekday))
    if endday_opening_hours:
        endday_opening_hours = endday_opening_hours[0]
        if endday_opening_hours.to_hour > end_datetime.time() > endday_opening_hours.from_hour:
            return True
    return False


def host_image(google_photo_ref):
    if google_photo_ref is None:
        return None
    api_url = 'https://maps.googleapis.com/maps/api/place/photo?maxheight=400&maxwidth=400&photoreference={}&key={}' \
        .format(google_photo_ref, 'AIzaSyD80xO_hx4nYwmRCVBL_uotZHm1udWDwRs')
    response = requests.get(api_url)
    host_api_url = 'https://api.imgbb.com/1/upload?key=8853b49ac4c262ec58a9849488dcb5a4'
    host_response = requests.post(
        host_api_url, files={'image': response.content})
    json_host_response = json.loads(host_response.text)
    return json_host_response['data']['url']


def request_save_details_of_places(place, api_key='AIzaSyD80xO_hx4nYwmRCVBL_uotZHm1udWDwRs'):
    # Return early if the opening hours are already saved.
    if OpeningHours.objects.filter(place=place).exists():
        return True
    # Place API : Place Details https://developers.google.com/maps/documentation/places/web-service/details#required-parameters
    api_url = 'https://maps.googleapis.com/maps/api/place/details/json?place_id={}&key={}&fields=opening_hours/periods,website,photos' \
        .format(place.google_id, api_key)
    response = requests.get(api_url)
    json_response = json.loads(response.text)
    if 'photos' in json_response['result']:
        place.image_url = host_image(
            json_response['result']['photos'][0]['photo_reference'])
    if 'website' in json_response['result']:
        place.website = json_response['result']['website']
    place.save()
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


def get_some_play(place, start_date, end_date, keywords):
    if General_Location_for_Play.objects.filter(name=place).exists():
        valid_places = General_Location_for_Play.objects.get(
            name=place).places.all()
    else:
        new_loc = General_Location_for_Play(name=place)
        new_loc.save()
        place_utils = Place_Utils(place, key_words=keywords)
        serializer = PlaceSerializer(
            data=place_utils.turn_to_model(), many=True)
        if serializer.is_valid():
            place_objects = serializer.save()
        valid_places = []
        print('retrieved places, now filtering')
        for place in place_objects:
            if not request_save_details_of_places(place):
                # The place has a wrongly formatted opening times, so just delete the place.
                place.delete()
                continue
            new_loc.places.add(place)
            valid_places.append(place)
    time_match_places = []
    for valid_place in valid_places:
        if check_time_availbility(
                start_date, end_date, OpeningHours.objects.filter(place=valid_place), valid_place.google_id):
            time_match_places.append(valid_place)
    return time_match_places


def get_some_eat(place, start_date, end_date, keywords):
    if General_Location_for_Eat.objects.filter(name=place).exists():
        valid_places = General_Location_for_Eat.objects.get(
            name=place).places.all()
    else:
        new_loc = General_Location_for_Eat(name=place)
        new_loc.save()
        place_utils = Place_Utils(place, key_words=keywords)
        serializer = PlaceSerializer(
            data=place_utils.turn_to_model(), many=True)
        if serializer.is_valid():
            place_objects = serializer.save()
        valid_places = []
        print('retrieved places, now filtering')
        for place in place_objects:
            if not request_save_details_of_places(place):
                # The place has a wrongly formatted opening times, so just delete the place.
                place.delete()
                continue
            new_loc.places.add(place)
            valid_places.append(place)
    time_match_places = []
    for valid_place in valid_places:
        if check_time_availbility(
                start_date, end_date, OpeningHours.objects.filter(place=valid_place), valid_place.google_id):
            time_match_places.append(valid_place)
    return time_match_places


def get_token_utils(place, start_time, end_time, play_keywords, eat_keywords, play_or_eat):
    token = sha256(place.encode('utf-8') + str(start_time).encode('utf-8') +
                   str(end_time).encode('utf-8') + str(random.randrange(10000)).encode('utf-8')).hexdigest()
    new_token = Token(number=token)
    new_token.save()
    json_format = {'play': {}, 'eat': {}}
    if play_or_eat == 0 or play_or_eat == 2:
        valid_places = get_some_play(
            place, start_time, end_time, play_keywords)
        available_categories = set()
        for place in valid_places:
            available_categories.add(place.category)
        indoor = {}
        id = 0
        for category in in_door_activities:
            if category in available_categories:
                indoor[category] = {'id': f'0-0-{id}', 'status': 1}
            else:
                indoor[category] = {'id': f'0-0-{id}', 'status': 0}
            id += 1
        outdoor = {}
        id = 0
        for category in out_door_activities:
            if category in available_categories:
                outdoor[category] = {'id': f'0-1-{id}', 'status': 1}
            else:
                outdoor[category] = {'id': f'0-1-{id}', 'status': 0}
            id += 1
        json_format['play'] = {"indoor": indoor, "outdoor": outdoor}
        new_token.categories = json.dumps(json_format)
        new_token.play_places.add(*valid_places)
        new_token.save()
    if play_or_eat == 1 or play_or_eat == 2:
        valid_places = get_some_eat(
            place, start_time, end_time, eat_keywords)
        new_token.eat_places.add(*valid_places)
    return token


def get_some_places_to_play_with_token(token):
    if Token.objects.filter(number=token).exists():
        valid_play = Token.objects.get(number=token).play_places.all()
        valid_eat = Token.objects.get(number=token).eat_places.all()
        return valid_play, valid_eat
    else:
        return None


def get_categories_for_token(token):
    if Token.objects.filter(number=token).exists():
        return Token.objects.get(number=token).categories
    else:
        return
