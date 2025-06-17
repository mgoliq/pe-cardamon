import unittest
from unittest.mock import MagicMock, patch

from public_transport_api.services.trips_service import get_trip_details


class TestGetTripDetails(unittest.TestCase):
    @patch('public_transport_api.services.trips_service.sqlite3.connect')
    def test_get_trip_details_success(self, mock_connect):
        # Mock database connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        # Mock trip info
        mock_cursor.fetchone.side_effect = [
            {'route_id': 'A', 'trip_headsign': 'KRZYKI'},  # trip info
        ]
        # Mock stop details
        mock_cursor.fetchall.return_value = [
            {
                'stop_name': 'Plac Grunwaldzki',
                'stop_lat': 51.1092,
                'stop_lon': 17.0415,
                'arrival_time': '2025-04-02T08:34:00Z',
                'departure_time': '2025-04-02T08:35:00Z'
            },
            {
                'stop_name': 'Renoma',
                'stop_lat': 51.1040,
                'stop_lon': 17.0280,
                'arrival_time': '2025-04-02T08:39:00Z',
                'departure_time': '2025-04-02T08:40:00Z'
            }
        ]

        trip_id = "3_14613060"
        result = get_trip_details(trip_id)
        self.assertIsNotNone(result)
        self.assertEqual(result['trip_id'], trip_id)
        self.assertEqual(result['route_id'], 'A')
        self.assertEqual(result['trip_headsign'], 'KRZYKI')
        self.assertEqual(len(result['stops']), 2)
        self.assertEqual(result['stops'][0]['name'], 'Plac Grunwaldzki')

if __name__ == '__main__':
    unittest.main()
