import sqlite3
from datetime import datetime
from typing import Dict, List


def haversine(lat1, lon1, lat2, lon2):
    # Calculate the great-circle distance between two points (in meters)
    from math import atan2, cos, radians, sin, sqrt
    R = 6371000  # Earth radius in meters
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c


def get_closest_departures(city: str, start_coordinates: str, end_coordinates: str, start_time: str, limit: int) -> List[Dict]:
    """
    Returns the closest departures from the start_coordinates, sorted by distance.
    Only supports city='wroclaw'.
    """
    if city.lower() != "wroclaw":
        return []

    try:
        start_lat, start_lon = map(float, start_coordinates.split(","))
        end_lat, end_lon = map(float, end_coordinates.split(","))
    except Exception:
        return []

    conn = None
    departures = []
    try:
        conn = sqlite3.connect("trips.sqlite")
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Find stops closest to start_coordinates
        cursor.execute("SELECT stop_id, stop_name, stop_lat, stop_lon FROM stops")
        stops = cursor.fetchall()

        stop_distances = []
        for stop in stops:
            dist = haversine(start_lat, start_lon, stop['stop_lat'], stop['stop_lon'])
            stop_distances.append((dist, stop))

        # Sort stops by distance and take the closest ones
        stop_distances.sort(key=lambda x: x[0])
        closest_stops = stop_distances[:limit]

        # For each closest stop, find a departure (mock: just pick the first trip for the stop)
        for dist, stop in closest_stops:
            cursor.execute("""
                SELECT t.trip_id, t.route_id, t.trip_headsign, st.arrival_time, st.departure_time
                FROM stop_times st
                JOIN trips t ON st.trip_id = t.trip_id
                WHERE st.stop_id = ?
                ORDER BY st.departure_time ASC
                LIMIT 1
            """, (stop['stop_id'],))
            trip_row = cursor.fetchone()
            if trip_row:
                departures.append({
                    "trip_id": trip_row['trip_id'],
                    "route_id": trip_row['route_id'],
                    "trip_headsign": trip_row['trip_headsign'],
                    "stop": {
                        "id": stop['stop_id'],
                        "name": stop['stop_name'],
                        "coordinates": {
                            "latitude": float(stop['stop_lat']),
                            "longitude": float(stop['stop_lon'])
                        },
                        "arrival_time": trip_row['arrival_time'],
                        "departure_time": trip_row['departure_time']
                    },
                    "distance_start_to_stop": dist,
                    "debug_dist_stop_to_end": haversine(stop['stop_lat'], stop['stop_lon'], end_lat, end_lon)
                })

        return departures

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return []
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return []
    finally:
        if conn:
            conn.close()
