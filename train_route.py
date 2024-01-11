import json
import math
import os
from pathlib import Path

import requests
from dotenv import load_dotenv

from roud_route import get_road_route

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


def get_train_route(origin: str, destination: str, avoid: str = "", mode: str = "transit",
                    transit_mode: str = 'rail', transit_routing_preference: str = "", option: int = 0):
    """

    :param option:
    :param origin:
    :param destination:
    :param avoid:
    :param mode:
    :param transit_mode:
    :param transit_routing_preference:
    :return:
    """
    origin = google_ready_keywords(origin)
    destination = google_ready_keywords(destination)

    cache_file_path = f"./Train_Response_Cache/Train_response_{origin.replace('+', ' ')}_to_{destination.replace('+', ' ')}.txt"

    if Path(cache_file_path).is_file():
        with open(cache_file_path, "r") as read_resp:
            resp = json.loads(read_resp.read())
    else:
        url = f"https://maps.googleapis.com/maps/api/directions/json?"
        params = {
            'origin': origin,
            'destination': destination,
            'avoid': avoid,
            'mode': mode,
            'transit_mode': transit_mode,
            'transit_routing_preference': transit_routing_preference,
            'key': GOOGLE_API_KEY
        }
        url += "&".join(f"{k}={v}" for k, v in params.items())

        headers = {'Content-Type': 'application/json'}
        resp = requests.get(url, headers=headers, timeout=60).json()

        with open(cache_file_path, "w") as f:
            f.write(json.dumps(resp))

    if resp.get('status') != 'OK':
        return "No Train Routes Found!"

    journey_info = extract_journey_info(resp)
    if journey_info.get('journey_transit_end'):
        if option != 0:
            if option == 3:
                cab_from_location_to_place = get_road_route(origin,
                                                            google_ready_keywords(journey_info['journey_transit_start']),
                                                            option=1)
                return journey_info, cab_from_location_to_place
            else:
                cab_from_place_to_location = get_road_route(google_ready_keywords(journey_info['journey_transit_end']),
                                                            destination, option=2)
                return journey_info, cab_from_place_to_location
        else:
            final_option = create_final_option(journey_info, origin, destination)
            return final_option

    return "No Train Routes Found!"


def extract_journey_info(resp):
    journey_transit_start = None
    journey_transit_end = None
    journey_transit_distance = 0
    journey_transit_duration = 0
    journey_transit_line = None
    for idx in range(0, len(resp['routes'][0]['legs'][0]['steps'])):
        # print(idx, "No of Iteration")
        if resp['routes'][0]['legs'][0]['steps'][idx]['travel_mode'] == "TRANSIT":
            if (resp['routes'][0]['legs'][0]['steps'][idx]['transit_details']['line']['vehicle']['name'] == "Train"
                    or "Subway" or "Tram"):
                if resp['routes'][0]['legs'][0]['steps'][idx]['transit_details']['line']['vehicle'][
                    'type'] == "HEAVY_RAIL":
                    if journey_transit_start is None:
                        journey_transit_start = \
                            resp['routes'][0]['legs'][0]['steps'][idx]['transit_details']['departure_stop']['name']
                    else:
                        pass
                    journey_transit_end = \
                        resp['routes'][0]['legs'][0]['steps'][idx]['transit_details']['arrival_stop']['name']
                    journey_transit_distance += float(
                        resp['routes'][0]['legs'][0]['steps'][idx]['distance']['text'].split()[0].replace(',', ''))
                    journey_transit_duration += resp['routes'][0]['legs'][0]['steps'][idx]['duration']['value']
                    if journey_transit_line is None:
                        journey_transit_line = \
                            resp['routes'][0]['legs'][0]['steps'][idx]['transit_details']['line'][
                                'name']
    train_journey_info = {
        "journey_origin": resp['routes'][0]['legs'][0]['start_address'],
        "journey_destination": resp['routes'][0]['legs'][0]['end_address'],
        "journey_transit_line": journey_transit_line,
        "journey_transit_distance": f"{round(journey_transit_distance)} km",
        "journey_transit_duration": journey_transit_duration,
        "journey_transit_start": journey_transit_start,
        "journey_transit_end": journey_transit_end
    }
    return train_journey_info


def create_final_option(journey_info, origin, destination):
    cab_from_location_to_place = get_road_route(origin, google_ready_keywords(journey_info['journey_transit_start']),
                                                option=1)
    cab_from_place_to_location = get_road_route(google_ready_keywords(journey_info['journey_transit_end']),
                                                destination, option=2)
    if float(cab_from_location_to_place['journey_transit_distance'].split()[0]) > 1.0:
        hours = cab_from_location_to_place['journey_transit_duration'] / (60 * 60)
        total_hours = hours
        rounded_hours = math.floor(total_hours)
        remaining_minutes = (total_hours - rounded_hours) * 60
        final_option_line_0 = "Take a Cab for {} from {} towards {} for {}, ".format(
            cab_from_location_to_place['journey_transit_distance'],
            ''.join(cab_from_location_to_place['journey_origin']).replace(",  ", ", "),
            journey_info['journey_transit_start'].split(",")[0],
            f"{rounded_hours} hours {int(remaining_minutes)} mins" if rounded_hours != 0 else f"{int(remaining_minutes)} mins")
    else:
        final_option_line_0 = "Walk for {} from {} towards {}, ".format(
            cab_from_location_to_place['journey_transit_distance'],
            ''.join(cab_from_location_to_place['journey_origin']).replace(",  ", ", "),
            journey_info['journey_transit_start'].split(",")[0],
        )
    hours = journey_info["journey_transit_duration"] / (60 * 60)
    total_hours = hours
    rounded_hours = math.floor(total_hours)
    remaining_minutes = (total_hours - rounded_hours) * 60
    final_option_line_1 = "Board the Train for {} from {} to {} for {}, ".format(
        journey_info['journey_transit_distance'],
        journey_info['journey_transit_start'].split(",")[0],
        journey_info['journey_transit_end'].split(",")[0],
        f"{int(rounded_hours)} hours {int(remaining_minutes)} mins")
    if int(cab_from_place_to_location['journey_transit_duration']) > 600:
        hours = cab_from_place_to_location['journey_transit_duration'] / (60 * 60)
        total_hours = hours
        rounded_hours = math.floor(total_hours)
        remaining_minutes = (total_hours - rounded_hours) * 60
        final_option_line_2 = "Take a Cab for {} from {} towards {} for {}.".format(
            cab_from_place_to_location['journey_transit_distance'],
            journey_info['journey_transit_end'].split(",")[0],
            ''.join(cab_from_place_to_location['journey_destination']).replace(",  ", ", "),
            f"{rounded_hours} hours {int(remaining_minutes)} mins" if rounded_hours != 0 else f"{int(remaining_minutes)} mins")
    else:
        final_option_line_2 = "Walk for {} from {} towards {}.".format(
            cab_from_place_to_location['journey_transit_distance'],
            journey_info['journey_transit_end'].split(",")[0],
            ''.join(cab_from_place_to_location['journey_destination']).replace(",  ", ", "),
        )
    final_option = final_option_line_0 + final_option_line_1 + final_option_line_2
    return final_option
