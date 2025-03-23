import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from dgt_rpc import DgtPOSClient, DgtException

class TestDgtPOSClient(unittest.TestCase):
    """Test cases for the DgtPOSClient class."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create a POS client with mocked connections
        self.pos_client = DgtPOSClient(
            url="https://test.dgtera.com",
            db="admin_db",
            api_key="admin_api_key"
        )
        
        # Mock the XML-RPC connections
        self.common_mock = MagicMock()
        self.models_mock = MagicMock()
        
        # Setup authentication response
        self.common_mock.authenticate.return_value = 1  # User ID
        
        # Patch the _get_connection methods
        patcher1 = patch.object(self.pos_client, '_get_common_connection', return_value=self.common_mock)
        patcher2 = patch.object(self.pos_client, '_get_models_connection', return_value=self.models_mock)
        
        # Start the patchers
        self.addCleanup(patcher1.stop)
        self.addCleanup(patcher2.stop)
        patcher1.start()
        patcher2.start()
        
        # Authenticate the client
        self.pos_client.authenticate()

    def test_get_pos_data(self):
        """Test getting POS configuration data."""
        # Setup mock response
        mock_pos_data = [
            {
                'id': 1,
                'name': 'Main POS',
                'pos_ID': 'POS001',
                'pos_name': 'Main POS',
                'active': True,
                'pos_type': 'pos'
            },
            {
                'id': 2,
                'name': 'Secondary POS',
                'pos_ID': 'POS002',
                'pos_name': 'Secondary POS',
                'active': True,
                'pos_type': 'pos'
            }
        ]
        self.models_mock.execute_kw.return_value = mock_pos_data
        
        # Call get_pos_data method
        result = self.pos_client.get_pos_data("retail_db")
        
        # Check that execute_kw was called with correct parameters
        self.models_mock.execute_kw.assert_called_once_with(
            "admin_db", 1, "admin_api_key",
            "pos.config", "get_pos_data",
            ["retail_db", True]
        )
        
        # Check that the result is correct
        self.assertEqual(result, mock_pos_data)

    def test_get_pos_orders(self):
        """Test getting POS orders."""
        # Setup mock response
        mock_orders = {
            'newest': [{'id': 101, 'name': 'Order 1', 'date_order': '2023-01-01 10:00:00'}],
            'oldest': [{'id': 1, 'name': 'Order 0001', 'date_order': '2022-01-01 09:00:00'}],
            'all': [
                {'id': 101, 'name': 'Order 1', 'date_order': '2023-01-01 10:00:00'},
                {'id': 1, 'name': 'Order 0001', 'date_order': '2022-01-01 09:00:00'}
            ]
        }
        self.models_mock.execute_kw.return_value = mock_orders
        
        # Call get_pos_orders method with a POS config dictionary
        pos_config = {'id': 1, 'pos_name': 'Main POS'}
        result = self.pos_client.get_pos_orders(pos_config, "retail_db", limit=10, include_lines=True)
        
        # Check that execute_kw was called with correct parameters
        self.models_mock.execute_kw.assert_called_once_with(
            "admin_db", 1, "admin_api_key",
            "pos.order", "get_pos_orders",
            [1, "retail_db", 10, True]
        )
        
        # Check that the result is correct
        self.assertEqual(result, mock_orders)

    def test_get_pos_orders_with_id(self):
        """Test getting POS orders using a POS ID instead of config dict."""
        # Setup mock response
        mock_orders = {
            'newest': [{'id': 101, 'name': 'Order 1', 'date_order': '2023-01-01 10:00:00'}],
            'oldest': [{'id': 1, 'name': 'Order 0001', 'date_order': '2022-01-01 09:00:00'}],
            'all': [
                {'id': 101, 'name': 'Order 1', 'date_order': '2023-01-01 10:00:00'},
                {'id': 1, 'name': 'Order 0001', 'date_order': '2022-01-01 09:00:00'}
            ]
        }
        self.models_mock.execute_kw.return_value = mock_orders
        
        # Call get_pos_orders method with a POS ID
        pos_id = 1
        result = self.pos_client.get_pos_orders(pos_id, "retail_db", limit=5, include_lines=False)
        
        # Check that execute_kw was called with correct parameters
        self.models_mock.execute_kw.assert_called_once_with(
            "admin_db", 1, "admin_api_key",
            "pos.order", "get_pos_orders",
            [1, "retail_db", 5, False]
        )
        
        # Check that the result is correct
        self.assertEqual(result, mock_orders)


if __name__ == '__main__':
    unittest.main() 