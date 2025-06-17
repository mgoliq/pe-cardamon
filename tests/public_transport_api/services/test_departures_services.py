import unittest
from unittest.mock import MagicMock, patch

from public_transport_api.services.departures_service import \
    get_closest_departures


class TestDeparturesService(unittest.TestCase):

    @patch('public_transport_api.services.departures_service.sqlite3.connect')
    def test_get_closest_departures_success(self, mock_connect):
        # Mock database connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        # Mock stops returned from DB
        mock_cursor.fetchall.side_effect = [
            [
                {'stop_id': '1', 'stop_name': 'Stop A', 'stop_lat': 51.1, 'stop_lon': 17.0},
                {'stop_id': '2', 'stop_name': 'Stop B', 'stop_lat': 51.2, 'stop_lon': 17.1}
            ],
            # For stop_times fetchall (not used, as fetchone is used)
        ]
        # Mock fetchone for trip info
        def fetchone_side_effect(*args, **kwargs):
            if "SELECT t.trip_id" in mock_cursor.execute.call_args[0][0]:
                return {
                    'trip_id': 'T1',
                    'route_id': 'R1',
                    'trip_headsign': 'HEAD',
                    'arrival_time': '08:00',
                    'departure_time': '08:05'
                }
            return None
        mock_cursor.fetchone.side_effect = fetchone_side_effect

        result = get_closest_departures(
            city="wroclaw",
            start_coordinates="51.1000,17.0000",
            end_coordinates="51.2000,17.1000",
            start_time="2025-06-17T08:00:00",
            limit=2
        )

        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)
        self.assertIn('trip_id', result[0])
        self.assertIn('stop', result[0])
        self.assertIn('distance_start_to_stop', result[0])

if __name__ == '__main__':
    unittest.main()
