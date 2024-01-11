import json
import math
import os
from pathlib import Path

import requests
from amadeus import Client
from dotenv import load_dotenv

from roud_route import get_road_route
from train_route import get_train_route

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_MAPS_KEY")
assert GOOGLE_API_KEY, "Google Maps API Key is missing from .env"

AIRLABS_API_KEY = os.getenv("AIRLABS_API_KEY")
assert AIRLABS_API_KEY, "Airlabs API Key is missing from .env"

amadeus = Client(
    client_id=os.getenv("AMADEUS_CLIENT_ID"),
    client_secret=os.getenv("AMADEUS_CLIENT_SECRET"),
)


def google_ready_keywords(place):
    """

    :param place:
    :return:
    """
    if len(place.split()) > 1:
        return place.replace(" ", "+")
    else:
        return place


def get_flight_route(origin: str, destination: str):
    """

    :param origin:
    :param destination:
    :return:
    """
    origin = google_ready_keywords(origin)
    destination = google_ready_keywords(destination)

    origin_address_record, origin_address = get_address_response(origin, 'Origin')
    destination_address_record, destination_address = get_address_response(destination, 'Destination')

    booking_request = determine_booking_request(origin_address_record, destination_address_record)

    origin_location, origin_airports_data = get_nearby_airports_data_amadeus(origin_address)
    destination_location, destination_airports_data = get_nearby_airports_data_amadeus(destination_address)

    if origin_airports_data and destination_airports_data:
        final_option = generate_final_option(booking_request, origin, origin_airports_data, destination,
                                             destination_airports_data)
        return final_option

    return "No Flights Routes Found!"


def get_address_response(address, address_type):
    saved_resp = Path(f"./Valid_Address_Response_Cache/{address_type}_response_{address.replace('+', ' ')}.txt")
    if saved_resp.is_file():
        read_resp = open(f"./Valid_Address_Response_Cache/{address_type}_response_{address.replace('+', ' ')}.txt", "r")
        address_data = json.loads(read_resp.read())
        read_resp.close()
    else:
        url = f"https://maps.googleapis.com/maps/api/geocode/json?address={address}&components=country&key={GOOGLE_API_KEY}"
        headers = {'Content-Type': 'application/json'}
        address_data = requests.get(url, headers=headers, timeout=60).json()['results'][0]
        f = open(f"./Valid_Address_Response_Cache/{address_type}_response_{address.replace('+', ' ')}.txt", "a")
        f.write(json.dumps(address_data))
        f.close()
    address_record = address_data['address_components'][len(address_data['address_components']) - 2]['short_name']
    return address_record, address_data


def determine_booking_request(origin_record, destination_record):
    if origin_record == destination_record:
        # print("Domestic Search")
        return "Domestic Search"
    else:
        # print("International Search")
        return "International Search"


def get_nearby_airports_data_airlabs(address_data):
    location = [address_data['geometry']['location']['lat'], address_data['geometry']['location']['lng']]
    saved_resp = Path(
        f"./Airlabs_Airport_Response_Cache/Nearby_Airports_({location[0]}, {location[1]}).txt")
    if saved_resp.is_file():
        read_resp = open(
            f"./Airlabs_Airport_Response_Cache/Nearby_Airports_({location[0]}, {location[1]}).txt",
            "r")
        airports_data = json.loads(read_resp.read())
        read_resp.close()
    else:
        kwargs = {"lat": location[0], "lng": location[1], "distance": 50, "api_key": AIRLABS_API_KEY}
        url = 'https://airlabs.co/api/v9/nearby'
        airports_data = requests.get(url, headers={'Content-Type': 'application/json'}, data=kwargs).json()['response'][
            'airports']
        f = open(
            f"./Airlabs_Airport_Response_Cache/Nearby_Airports_({location[0]}, {location[1]}).txt",
            "a")
        f.write(json.dumps(airports_data))
        f.close()

    return location, airports_data


def get_nearby_airports_data_amadeus(address_data):
    location = [address_data['geometry']['location']['lat'], address_data['geometry']['location']['lng']]
    saved_resp = Path(
        f"./Amadeus_Airport_Response_Cache/Nearby_Airports_({location[0]}, {location[1]}).txt")
    if saved_resp.is_file():
        read_resp = open(
            f"./Amadeus_Airport_Response_Cache/Nearby_Airports_({location[0]}, {location[1]}).txt",
            "r")
        airports_data = json.loads(read_resp.read())
        read_resp.close()
    else:
        kwargs = {"latitude": location[0], "longitude": location[1]}
        origin_response = amadeus.reference_data.locations.airports.get(**kwargs)
        airports_data = origin_response.data
        f = open(
            f"./Amadeus_Airport_Response_Cache/Nearby_Airports_({location[0]}, {location[1]}).txt",
            "a")
        f.write(json.dumps(airports_data))
        f.close()

    return location, airports_data


def generate_final_option(booking_request, origin, origin_airports_data, destination, destination_airports_data):
    origin_airport_info, origin_airport_distance = (
        f"{origin_airports_data[0]['name']} {origin_airports_data[0]['subType']}, {origin_airports_data[0]['address']['cityName']}" if booking_request == 'International Search' else \
            origin_airports_data[0]['name'], origin_airports_data[0]['distance']['value'])
    destination_airport_info, destination_airport_distance = (
        f"{destination_airports_data[0]['name']} {destination_airports_data[0]['subType']}, {destination_airports_data[0]['address']['cityName']}" if booking_request == 'International Search' else \
            destination_airports_data[0]['name'], destination_airports_data[0]['distance']['value'])

    if origin_airport_distance > 10:
        travel_from_location_to_place = get_train_route(origin, origin_airport_info, option=3)
        final_option_cab = generate_option_line_cab(travel_from_location_to_place[1],
                                                    travel_from_location_to_place[1]['journey_destination'], 1)
        final_option_train = generate_option_line_cab_rail(travel_from_location_to_place[0], origin_airport_info, 1)
        final_option_line_0 = final_option_cab + final_option_train
    else:
        cab_from_location_to_place = get_road_route(origin, origin_airport_info, option=1)
        final_option_line_0 = generate_option_line_cab(cab_from_location_to_place, origin_airport_info, 1)

    if destination_airport_distance > 10:
        travel_from_place_to_location = get_train_route(destination_airport_info, destination, option=4)
        final_option_train = generate_option_line_cab(travel_from_place_to_location[1], destination_airport_info, 2)
        final_option_cab = generate_option_line_rail(travel_from_place_to_location[0],
                                                     travel_from_place_to_location[0]['journey_origin'], 2)
        final_option_line_2 = final_option_train + final_option_cab
    else:
        cab_from_place_to_location = get_road_route(destination_airport_info, destination, option=2)
        final_option_line_2 = generate_option_line_cab(cab_from_place_to_location, destination_airport_info, 2)
    final_option_line_1 = "Board the Airplane from {} to {}, ".format(origin_airport_info, destination_airport_info)
    final_option = final_option_line_0 + final_option_line_1 + final_option_line_2
    return final_option


def generate_option_line_cab(route_info, location_info, trip_no):
    if trip_no == 1:
        if float(route_info['journey_transit_distance'].split()[0]) > 1.0:
            hours = route_info['journey_transit_duration'] / (60 * 60)
            total_hours = hours
            rounded_hours = math.floor(total_hours)
            remaining_minutes = (total_hours - rounded_hours) * 60
            return "Take a Cab for {} from {} towards {} for {}, ".format(
                route_info['journey_transit_distance'],
                ''.join(route_info['journey_origin']).replace(',  ', ', '),
                ''.join(location_info).replace(',  ', ', ') if len(location_info) > 1 else location_info[0],
                f"{rounded_hours} hours {int(remaining_minutes)} mins" if rounded_hours != 0 else f"{int(remaining_minutes)} mins")
        else:
            return "Walk for {} from {} towards {}, ".format(
                route_info['journey_transit_distance'],
                ''.join(route_info['journey_origin']).replace(',  ', ', '),
                ''.join(location_info).replace(',  ', ', ') if len(location_info) > 1 else location_info[0])
    else:
        if float(route_info['journey_transit_distance'].split()[0]) > 1.0:
            hours = route_info['journey_transit_duration'] / (60 * 60)
            total_hours = hours
            rounded_hours = math.floor(total_hours)
            remaining_minutes = (total_hours - rounded_hours) * 60
            return "Take a Cab for {} from {} towards {} for {}.".format(
                route_info['journey_transit_distance'],
                ''.join(location_info).replace(',  ', ', ') if len(location_info) > 1 else location_info[0],
                ''.join(route_info['journey_destination']).replace(',  ', ', '),
                f"{rounded_hours} hours {int(remaining_minutes)} mins" if rounded_hours != 0 else f"{int(remaining_minutes)} mins")
        else:
            return "Walk for {} from {} towards {}.".format(
                route_info['journey_transit_distance'],
                ''.join(location_info).replace(',  ', ', ') if len(location_info) > 1 else location_info[0],
                ''.join(route_info['journey_destination']).replace(',  ', ', '))


def generate_option_line_rail(route_info, location_info, trip_no):
    if trip_no == 1:
        if int(route_info['journey_transit_duration']) > 600:
            hours = route_info['journey_transit_duration'] / (60 * 60)
            total_hours = hours
            rounded_hours = math.floor(total_hours)
            remaining_minutes = (total_hours - rounded_hours) * 60
            return "Take a Rail for {} from {} towards {} for {}, ".format(
                route_info['journey_transit_distance'],
                ''.join(route_info['journey_origin']).replace(',  ', ', '),
                ''.join(location_info).replace(',  ', ', ') if len(location_info) > 1 else location_info[0],
                f"{rounded_hours} hours {int(remaining_minutes)} mins" if rounded_hours != 0 else f"{int(remaining_minutes)} mins")
        else:
            return "Walk for {} from {} towards {}, ".format(
                route_info['journey_transit_distance'],
                ''.join(route_info['journey_origin']).replace(',  ', ', '),
                ''.join(location_info).replace(',  ', ', ') if len(location_info) > 1 else location_info[0])
    else:
        if int(route_info['journey_transit_duration']) > 600:
            hours = route_info['journey_transit_duration'] / (60 * 60)
            total_hours = hours
            rounded_hours = math.floor(total_hours)
            remaining_minutes = (total_hours - rounded_hours) * 60
            return "Take a Rail for {} from {} towards {} for {}.".format(
                route_info['journey_transit_distance'],
                ''.join(location_info).replace(',  ', ', ') if len(location_info) > 1 else location_info[0],
                ''.join(route_info['journey_destination']).replace(',  ', ', '),
                f"{rounded_hours} hours {int(remaining_minutes)} mins" if rounded_hours != 0 else f"{int(remaining_minutes)} mins")
        else:
            return "Walk for {} from {} towards {}.".format(
                route_info['journey_transit_distance'],
                ''.join(location_info).replace(',  ', ', ') if len(location_info) > 1 else location_info[0],
                ''.join(route_info['journey_destination']).replace(',  ', ', '))


def generate_option_line_cab_rail(route_info, location_info, trip_no):
    if trip_no == 1:
        if int(route_info['journey_transit_duration']) > 600:
            hours = route_info['journey_transit_duration'] / (60 * 60)
            total_hours = hours
            rounded_hours = math.floor(total_hours)
            remaining_minutes = (total_hours - rounded_hours) * 60
            return "Take a Rail for {} from {} towards {} for {}, ".format(
                route_info['journey_transit_distance'],
                ''.join(route_info['journey_transit_start']).replace(',  ', ', '),
                ''.join(location_info).replace(',  ', ', ') if len(location_info) > 1 else location_info[0],
                f"{rounded_hours} hours {int(remaining_minutes)} mins" if rounded_hours != 0 else f"{int(remaining_minutes)} mins")
        else:
            return "Walk for {} from {} towards {}, ".format(
                route_info['journey_transit_distance'],
                ''.join(route_info['journey_origin']).replace(',  ', ', '),
                ''.join(location_info).replace(',  ', ', ') if len(location_info) > 1 else location_info[0])
    else:
        if int(route_info['journey_transit_duration']) > 600:
            hours = route_info['journey_transit_duration'] / (60 * 60)
            total_hours = hours
            rounded_hours = math.floor(total_hours)
            remaining_minutes = (total_hours - rounded_hours) * 60
            return "Take a Rail for {} from {} towards {} for {}.".format(
                route_info['journey_transit_distance'],
                ''.join(location_info).replace(',  ', ', ') if len(location_info) > 1 else location_info[0],
                ''.join(route_info['journey_transit_end']).replace(',  ', ', '),
                f"{rounded_hours} hours {int(remaining_minutes)} mins" if rounded_hours != 0 else f"{int(remaining_minutes)} mins")
        else:
            return "Walk for {} from {} towards {}.".format(
                route_info['journey_transit_distance'],
                ''.join(location_info).replace(',  ', ', ') if len(location_info) > 1 else location_info[0],
                ''.join(route_info['journey_destination']).replace(',  ', ', '))
