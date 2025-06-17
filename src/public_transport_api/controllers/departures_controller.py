from datetime import datetime

from flask import Blueprint, jsonify, request

from public_transport_api.services.departures_service import \
    get_closest_departures

departures_bp = Blueprint('departures', __name__, url_prefix='/public_transport/city/<string:city>/closest_departures')

@departures_bp.route("/", methods=["GET"])
def closest_departures(city):
    """
    The endpoint returns the closest departures of lines that bring the user closer to the destination.
    Lines that start in the opposite direction shall not be displayed.
    Departures are sorted by distance from start_coordinates in ascending order (the closest first).
    The endpoint does not consider which line brings the user closer to the destination.

    Request Parameters:
        Path Parameters:
        - city (required): The city for the public transport search. Currently, only "wroclaw" is supported.
        Query Parameters:
        - start_coordinates (required): The geolocation coordinates where the user wants to start the trip.
        - end_coordinates (required): The geolocation coordinates where the user wants to finish the trip.
        - start_time (optional, default: current time): The time at which the user starts the trip.
        - limit (optional, default: 5): The maximum number of departures to be returned.
    """
    # Handle request parameters and add the metadata. Include error handling.
    try:
        if city.lower() != "wroclaw":
            return jsonify({"error": "Only 'wroclaw' is supported."}), 400

        start_coordinates = request.args.get("start_coordinates")
        end_coordinates = request.args.get("end_coordinates")
        start_time = request.args.get("start_time", datetime.now().isoformat())
        limit = int(request.args.get("limit", 5))

        if not start_coordinates or not end_coordinates:
            return jsonify({"error": "Missing required parameters: start_coordinates and end_coordinates."}), 400

        # Optionally, validate coordinates format here

        departures = get_closest_departures(
            city=city,
            start_coordinates=start_coordinates,
            end_coordinates=end_coordinates,
            start_time=start_time,
            limit=limit
        )
        return jsonify({
            "metadata": {
                "city": city,
                "start_coordinates": start_coordinates,
                "end_coordinates": end_coordinates,
                "start_time": start_time,
                "limit": limit
            },
            "departures": departures
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500