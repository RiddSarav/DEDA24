from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
import requests

def get_ip_location():
    ip_info = requests.get('https://ipinfo.io').json()
    return ip_info['loc'].split(',')
def get_road_name(latitude, longitude):
    geolocator = Nominatim(user_agent="work")
    try:
        location = geolocator.reverse((latitude, longitude), exactly_one=True)
        address = location.raw.get('address')
        if address and 'road' in address:
            return address['road']
        else:
            return "Road name not found."
    except (GeocoderTimedOut, KeyError) as e:
        return "Error: {}".format(str(e))
if __name__ == "__main__":
    location = get_ip_location()
    latitude, longitude = location
    print("Latitude:", latitude)
    print("Longitude:", longitude)
    road_name = get_road_name(latitude, longitude)
    print("The road is:", road_name)
