from typing import List, Dict  # Import List and Dict for type hints
import sqlite3

def get_closest_departures(city: str, start_coordinates: str, end_coordinates: str, start_time: str, limit: int) -> List[Dict]:
    """
    Optimized version to fetch closest departures.
    """
    if city.lower() != "wroclaw":
        return []

    try:
        start_lat, start_lon = map(float, start_coordinates.split(","))
        end_lat, end_lon = map(float, end_coordinates.split(","))
    except ValueError:
        return []

    conn = None
    departures = []
    try:
        conn = sqlite3.connect("trips.sqlite")
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Optimize query by calculating distances directly in SQL
        query = """
            SELECT 
                stops.stop_id, stops.stop_name, stops.stop_lat, stops.stop_lon,
                t.trip_id, t.route_id, t.trip_headsign, st.arrival_time, st.departure_time,
                ((stops.stop_lat - ?) * (stops.stop_lat - ?) + (stops.stop_lon - ?) * (stops.stop_lon - ?)) AS distance
            FROM stops
            JOIN stop_times st ON stops.stop_id = st.stop_id
            JOIN trips t ON st.trip_id = t.trip_id
            WHERE stops.stop_lat BETWEEN ? AND ?
              AND stops.stop_lon BETWEEN ? AND ?
              AND st.departure_time >= ?
            ORDER BY distance ASC
            LIMIT ?
        """
        # Define bounds for filtering stops (e.g., +/- 0.1 degrees for latitude/longitude)
        lat_range = 0.1
        lon_range = 0.1
        cursor.execute(query, (
            start_lat, start_lat, start_lon, start_lon,
            start_lat - lat_range, start_lat + lat_range,
            start_lon - lon_range, start_lon + lon_range,
            start_time, limit
        ))

        rows = cursor.fetchall()
        for row in rows:
            departures.append({
                "trip_id": row["trip_id"],
                "route_id": row["route_id"],
                "trip_headsign": row["trip_headsign"],
                "stop": {
                    "name": row["stop_name"],
                    "coordinates": {
                        "latitude": row["stop_lat"],
                        "longitude": row["stop_lon"]
                    },
                    "arrival_time": row["arrival_time"],
                    "departure_time": row["departure_time"]
                }
            })
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        if conn:
            conn.close()

    return departures
