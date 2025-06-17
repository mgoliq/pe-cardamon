import sqlite3


def get_trip_details(trip_id):
    """
    Retrieves trip details from the database, including route, headsign, and all stops for the trip.
    Returns None if not found.
    """
    conn = None
    try:
        conn = sqlite3.connect('trips.sqlite')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Get trip info
        cursor.execute("""
            SELECT route_id, trip_headsign FROM trips WHERE trip_id = ?
        """, (trip_id,))
        trip_row = cursor.fetchone()
        if not trip_row:
            return None

        route_id = trip_row['route_id']
        trip_headsign = trip_row['trip_headsign']

        # Get stop details for the trip, ordered by stop_sequence
        cursor.execute("""
            SELECT st.arrival_time, st.departure_time, s.stop_name, s.stop_lat, s.stop_lon
            FROM stop_times st
            JOIN stops s ON st.stop_id = s.stop_id
            WHERE st.trip_id = ?
            ORDER BY st.stop_sequence ASC
        """, (trip_id,))
        stops = []
        for row in cursor.fetchall():
            stops.append({
                "name": row['stop_name'],
                "coordinates": {
                    "latitude": float(row['stop_lat']),
                    "longitude": float(row['stop_lon'])
                },
                "arrival_time": row['arrival_time'],
                "departure_time": row['departure_time']
            })

        return {
            "trip_id": trip_id,
            "route_id": route_id,
            "trip_headsign": trip_headsign,
            "stops": stops
        }
    except Exception as e:
        print(f"Error in get_trip_details: {e}")
        return None
    finally:
        if conn:
            conn.close()

