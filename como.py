import googlemaps
from datetime import datetime
import sqlite3

# Replace 'YOUR_API_KEY' with your actual Google Maps API key
gmaps = googlemaps.Client(key='AIzaSyBke_l1WuwK53D_E1qOJCarDVIKsQRwEm4')


def get_directions(start_point, end_point):
    directions = gmaps.directions(start_point, end_point, mode="driving", departure_time=datetime.now())
    return directions


def check_against_database(directions, db_path, threshold):
    route = directions[0]['legs'][0]['steps']
    route_names = [step['html_instructions'] for step in route]

    matching_roads = {}
    conn = sqlite3.connect(db_path)  # Connect to the database
    cursor = conn.cursor()

    # Define a query to select roads from the database (use correct table name)
    query = "SELECT road, bumpiness FROM road_bumpiness WHERE LOWER(road) IN (?)"
    cursor.execute(query, [", ".join(route_names).lower()])  # Convert route names to lowercase and comma-separated string

    for row in cursor.fetchall():
        road, bumpiness = row
        if bumpiness > threshold:
            matching_roads[road] = bumpiness

    cursor.close()
    conn.close()  # Close the connection

    return matching_roads


def avoid_roads(directions, roads_to_avoid):
    waypoints = []
    for step in directions[0]['legs'][0]['steps']:
        instruction = step['html_instructions']
        for road, _ in roads_to_avoid.items():
            if road.lower() in instruction.lower():
                waypoints.append(step['end_location'])
                break

    # Remove duplicate waypoints
    unique_waypoints = []
    for waypoint in waypoints:
        if waypoint not in unique_waypoints:
            unique_waypoints.append(waypoint)

    if unique_waypoints:
        # Generate a new set of directions avoiding the specified roads
        new_directions = gmaps.directions(
            directions[0]['legs'][0]['start_location'],
            directions[0]['legs'][0]['end_location'],
            mode="driving",
            departure_time=datetime.now(),
            waypoints=unique_waypoints,
            optimize_waypoints=True
        )
        return new_directions
    else:
        # If no roads to avoid, return original directions
        return directions


def main(start_point, end_point):
    # Example start and end points

    # Path to the database file (replace with your actual path)
    db_path = "road_data.db"

    threshold = 6.0

    directions = get_directions(start_point, end_point)
    roads_to_avoid = check_against_database(directions, db_path, threshold)

    if roads_to_avoid:
        new_directions = avoid_roads(directions, roads_to_avoid)

        # Print the new directions
        print("New Directions after rerouting to avoid the mentioned roads:")
        for step in new_directions[0]['legs'][0]['steps']:
            print(step['html_instructions'])
    else:
        # If no roads to avoid, print the original directions
        print("Original Directions:")
        for step in directions[0]['legs'][0]['steps']:
            print(step['html_instructions'])


if __name__ == "__main__":
    start=input("where do you want to start from")
    end=input("where is your destination")
    main(start_point=start, end_point=end)
