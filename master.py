import socket
import sqlite3
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
import requests

def create_database():
    conn = sqlite3.connect('road_data.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS road_bumpiness
                 (road TEXT, bumpiness INTEGER)''')
    conn.commit()
    conn.close()

def insert_data(road, bumpiness):
    conn = sqlite3.connect('road_data.db')
    c = conn.cursor()
    c.execute("INSERT INTO road_bumpiness (road, bumpiness) VALUES (?, ?)", (road, bumpiness))
    conn.commit()
    conn.close()

def connect_road_bumpiness():
    conn = sqlite3.connect('road_data.db')
    c = conn.cursor()
    c.execute("SELECT * FROM road_bumpiness")
    rows = c.fetchall()
    print("Road\tBumpiness")
    for row in rows:
        print(f"{row[0]}\t{row[1]}")
    conn.close()

def get_ip_location():
    ip_info = requests.get('https://ipinfo.io/').json()
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

def main():
    create_database()

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ('192.168.1.44', 2217)  # Change the IP address and port as needed

    try:
        server_socket.bind(server_address)
        server_socket.listen(1)

        print('Waiting for a connection...')
        connection, client_address = server_socket.accept()
        print('Connected to:', client_address)

        while True:
            data = connection.recv(1024)
            if data:
                received_data = data.decode()
                bumpiness_rating = int(received_data)

                # Get IP location
                location = get_ip_location()
                latitude, longitude = location
                road_name = get_road_name(latitude, longitude)

                insert_data(road_name, bumpiness_rating)
                print('Road:', road_name)
                print('Bumpiness Rating:', bumpiness_rating)

    finally:
        connection.close()
        server_socket.close()

    connect_road_bumpiness()

if __name__ == "__main__":
    main()
