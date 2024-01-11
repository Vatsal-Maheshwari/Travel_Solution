import json
import math
import os

import requests
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_MAPS_KEY")
assert GOOGLE_API_KEY, "Google Maps API Key is missing from .env"


def google_ready_keywords(place):
    """

    :param place:
    :return:
    """
    if len(place.split()) > 1:
        return place.replace(" ", "+")
    else:
        return place


def get_road_route(origin: str, destination: str, avoid: str = "",
                   mode: str = "driving", transit_routing_preference: str = "", option: int = 0):
    """

    :param origin:
    :param destination:
    :param option:
    :param avoid:
    :param mode:
    :param transit_routing_preference:
    :return:
    """
    origin = google_ready_keywords(origin)
    destination = google_ready_keywords(destination)

    cache_filename = f"./Cab_Response_Cache/Cab_response_{origin.replace('+', ' ')}_{destination.replace('+', ' ')}.txt"
    try:
        with open(cache_filename, "r") as file:
            resp = json.load(file)
    except FileNotFoundError:
        params = {
            'origin': origin,
            'destination': destination,
            'avoid': avoid,
            'mode': mode,
            'transit_routing_preference': transit_routing_preference,
            'key': GOOGLE_API_KEY
        }
        url = "https://maps.googleapis.com/maps/api/directions/json?"
        resp = requests.get(url, params=params, timeout=60).json()
        with open(cache_filename, "w") as file:
            json.dump(resp, file)

    if resp.get('status') == 'OK':
        route = resp['routes'][0]['legs'][0]
        journey_info = {
            "journey_origin": route['start_address'].split(',')[0:-2],
            "journey_destination": route['end_address'].split(',')[0:-2],
            "journey_transit_distance": route['distance']['text'],
            "journey_transit_duration": route['duration']['value']
        }
        if option != 0:
            return journey_info
        else:
            hours = journey_info['journey_transit_duration'] / 3600
            rounded_hours = math.floor(hours)
            remaining_minutes = (hours - rounded_hours) * 60

            final_option = f"Cab from {''.join(journey_info['journey_origin']).replace(',  ', '', )} towards {''.join(journey_info['journey_destination']).replace(',  ', '', )} "
            final_option += f"(Travel Duration: {rounded_hours} hours {int(remaining_minutes)} mins, "
            final_option += f"Travel Distance: {journey_info['journey_transit_distance']})."
            return final_option
    elif resp['status'] == 'ZERO_RESULTS' or resp['status'] == 'NOT_FOUND':
        if option != 0:
            cab_journey_info = {
                "journey_origin": origin.replace('+', ' '),
                "journey_destination": destination.replace('+', ' '),
                "journey_transit_distance": '0',
                "journey_transit_duration": 0
            }
            return cab_journey_info
        else:
            return "No Cab Routes Found!"
