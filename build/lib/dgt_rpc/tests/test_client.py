import unittest
from unittest.mock import patch, MagicMock
import xmlrpc.client
import os
import tempfile

from dgt_rpc import DgtClient, DgtException

class TestDgtClient(unittest.TestCase):
    """Test cases for the DgtClient class."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create a client with mocked connections
        self.client = DgtClient(
            url="https://test.dgtera.com",
            db="test_db",
            username="test_user",
            password="test_password"
        )
        
        # Mock the XML-RPC connections
        self.common_mock = MagicMock()
        self.models_mock = MagicMock()
        
        # Setup authentication response
        self.common_mock.authenticate.return_value = 1  # User ID
        
        # Patch the _get_connection methods
        patcher1 = patch.object(self.client, '_get_common_connection', return_value=self.common_mock)
        patcher2 = patch.object(self.client, '_get_models_connection', return_value=self.models_mock)
        
        # Start the patchers
        self.addCleanup(patcher1.stop)
        self.addCleanup(patcher2.stop)
        patcher1.start()
        patcher2.start()

    def test_authenticate_with_username_password(self):
        """Test authentication with username and password."""
        uid = self.client.authenticate()
        
        # Check that authenticate was called with correct parameters
        self.common_mock.authenticate.assert_called_once_with(
            "test_db", "test_user", "test_password", {}
        )
        
        # Check that the returned UID is correct
        self.assertEqual(uid, 1)
        
        # Check that the client's uid attribute was set
        self.assertEqual(self.client.uid, 1)

    def test_authenticate_with_api_key(self):
        """Test authentication with API key."""
        # Create a new client with API key
        client = DgtClient(
            url="https://test.dgtera.com",
            db="test_db",
            api_key="test_api_key"
        )
        
        # Mock the connections
        common_mock = MagicMock()
        common_mock.authenticate.return_value = 2  # Different user ID
        
        with patch.object(client, '_get_common_connection', return_value=common_mock):
            uid = client.authenticate()
            
            # Check that authenticate was called with correct parameters
            common_mock.authenticate.assert_called_once_with(
                "test_db", "admin", "test_api_key", {}
            )
            
            # Check that the returned UID is correct
            self.assertEqual(uid, 2)

    def test_search(self):
        """Test the search method."""
        # Setup mock response
        self.models_mock.execute_kw.return_value = [1, 2, 3]
        
        # Call search method
        result = self.client.search(
            model="res.partner",
            domain=[("customer_rank", ">", 0)],
            limit=10
        )
        
        # Check that execute_kw was called with correct parameters
        self.models_mock.execute_kw.assert_called_once_with(
            "test_db", 1, "test_password",
            "res.partner", "search",
            [("customer_rank", ">", 0)],
            {"limit": 10, "offset": 0, "order": None}
        )
        
        # Check that the result is correct
        self.assertEqual(result, [1, 2, 3])

    def test_read(self):
        """Test the read method."""
        # Setup mock response
        mock_data = [
            {"id": 1, "name": "Test Partner 1"},
            {"id": 2, "name": "Test Partner 2"}
        ]
        self.models_mock.execute_kw.return_value = mock_data
        
        # Call read method
        result = self.client.read(
            model="res.partner",
            ids=[1, 2],
            fields=["name"]
        )
        
        # Check that execute_kw was called with correct parameters
        self.models_mock.execute_kw.assert_called_once_with(
            "test_db", 1, "test_password",
            "res.partner", "read",
            [1, 2],
            {"fields": ["name"]}
        )
        
        # Check that the result is correct
        self.assertEqual(result, mock_data)

    def test_search_read(self):
        """Test the search_read method."""
        # Setup mock response
        mock_data = [
            {"id": 1, "name": "Test Partner 1"},
            {"id": 2, "name": "Test Partner 2"}
        ]
        self.models_mock.execute_kw.return_value = mock_data
        
        # Call search_read method
        result = self.client.search_read(
            model="res.partner",
            domain=[("customer_rank", ">", 0)],
            fields=["name"],
            limit=10
        )
        
        # Check that execute_kw was called with correct parameters
        self.models_mock.execute_kw.assert_called_once_with(
            "test_db", 1, "test_password",
            "res.partner", "search_read",
            [("customer_rank", ">", 0)],
            {"fields": ["name"], "limit": 10, "offset": 0, "order": None}
        )
        
        # Check that the result is correct
        self.assertEqual(result, mock_data)

    def test_create(self):
        """Test the create method."""
        # Setup mock response
        self.models_mock.execute_kw.return_value = 5  # New record ID
        
        # Call create method
        result = self.client.create(
            model="res.partner",
            values={"name": "New Partner", "email": "new@example.com"}
        )
        
        # Check that execute_kw was called with correct parameters
        self.models_mock.execute_kw.assert_called_once_with(
            "test_db", 1, "test_password",
            "res.partner", "create",
            [{"name": "New Partner", "email": "new@example.com"}],
            {}
        )
        
        # Check that the result is correct
        self.assertEqual(result, 5)

    def test_write(self):
        """Test the write method."""
        # Setup mock response
        self.models_mock.execute_kw.return_value = True
        
        # Call write method
        result = self.client.write(
            model="res.partner",
            ids=[1, 2],
            values={"name": "Updated Partner"}
        )
        
        # Check that execute_kw was called with correct parameters
        self.models_mock.execute_kw.assert_called_once_with(
            "test_db", 1, "test_password",
            "res.partner", "write",
            [1, 2],
            {"name": "Updated Partner"}
        )
        
        # Check that the result is correct
        self.assertTrue(result)

    def test_unlink(self):
        """Test the unlink method."""
        # Setup mock response
        self.models_mock.execute_kw.return_value = True
        
        # Call unlink method
        result = self.client.unlink(
            model="res.partner",
            ids=[1, 2]
        )
        
        # Check that execute_kw was called with correct parameters
        self.models_mock.execute_kw.assert_called_once_with(
            "test_db", 1, "test_password",
            "res.partner", "unlink",
            [1, 2],
            {}
        )
        
        # Check that the result is correct
        self.assertTrue(result)

    def test_execute(self):
        """Test the execute method."""
        # Setup mock response
        self.models_mock.execute_kw.return_value = {"state": "confirmed"}
        
        # Call execute method
        result = self.client.execute(
            model="sale.order",
            method="action_confirm",
            args=[5]  # Order ID as a named parameter
        )
        
        # Check that execute_kw was called with correct parameters
        self.models_mock.execute_kw.assert_called_once_with(
            "test_db", 1, "test_password",
            "sale.order", "action_confirm",
            [5],
            {}
        )
        
        # Check that the result is correct
        self.assertEqual(result, {"state": "confirmed"})

    def test_execute_kw(self):
        """Test the execute_kw method."""
        # Setup mock response
        self.models_mock.execute_kw.return_value = [{"id": 1, "name": "Product"}]
        
        # Call execute_kw method
        result = self.client.execute_kw(
            model="product.product",
            method="name_search",
            args=[],
            kwargs={"name": "Chair", "limit": 5}
        )
        
        # Check that execute_kw was called with correct parameters
        self.models_mock.execute_kw.assert_called_once_with(
            "test_db", 1, "test_password",
            "product.product", "name_search",
            [],
            {"name": "Chair", "limit": 5}
        )
        
        # Check that the result is correct
        self.assertEqual(result, [{"id": 1, "name": "Product"}])

    def test_create_batch(self):
        """Test the create_batch method."""
        # Setup mock responses for multiple calls
        self.models_mock.execute_kw.side_effect = [
            [101, 102],  # First batch
            [103]        # Second batch
        ]
        
        # Data to create
        values_list = [
            {"name": "Product 1", "list_price": 10},
            {"name": "Product 2", "list_price": 20},
            {"name": "Product 3", "list_price": 30}
        ]
        
        # Call create_batch method with batch_size=2
        result = self.client.create_batch(
            model="product.product",
            values_list=values_list,
            batch_size=2
        )
        
        # Check that execute_kw was called twice with correct parameters
        self.assertEqual(self.models_mock.execute_kw.call_count, 2)
        
        # First call should create the first two products
        self.models_mock.execute_kw.assert_any_call(
            "test_db", 1, "test_password",
            "product.product", "create",
            [{"name": "Product 1", "list_price": 10}, {"name": "Product 2", "list_price": 20}],
            {}
        )
        
        # Second call should create the third product
        self.models_mock.execute_kw.assert_any_call(
            "test_db", 1, "test_password",
            "product.product", "create",
            [{"name": "Product 3", "list_price": 30}],
            {}
        )
        
        # Check that the result combines both batches
        self.assertEqual(result, [101, 102, 103])

    def test_from_environment(self):
        """Test creating a client from environment variables."""
        # Set environment variables
        os.environ['DGTERA_URL'] = "https://env.dgtera.com"
        os.environ['DGTERA_DB'] = "env_db"
        os.environ['DGTERA_USERNAME'] = "env_user"
        os.environ['DGTERA_PASSWORD'] = "env_password"
        
        # Create client from environment
        with patch('xmlrpc.client.ServerProxy'):  # Mock ServerProxy to avoid actual connections
            client = DgtClient.from_environment()
            
            # Check that the client was configured correctly
            self.assertEqual(client.url, "https://env.dgtera.com")
            self.assertEqual(client.db, "env_db")
            self.assertEqual(client.username, "env_user")
            self.assertEqual(client.password, "env_password")
        
        # Clean up environment
        del os.environ['DGTERA_URL']
        del os.environ['DGTERA_DB']
        del os.environ['DGTERA_USERNAME']
        del os.environ['DGTERA_PASSWORD']

    def test_from_config(self):
        """Test creating a client from a configuration file."""
        # Create a temporary config file
        config_content = """
        [default]
        url = https://config.dgtera.com
        db = config_db
        username = config_user
        password = config_password
        
        [test]
        url = https://test-config.dgtera.com
        db = test_config_db
        api_key = test_config_api_key
        """
        
        with tempfile.NamedTemporaryFile(mode='w+', delete=False) as temp:
            temp.write(config_content)
            temp_path = temp.name
        
        try:
            # Create client from default profile
            with patch('xmlrpc.client.ServerProxy'):  # Mock ServerProxy to avoid actual connections
                client1 = DgtClient.from_config(config_file=temp_path)
                
                # Check that the client was configured correctly
                self.assertEqual(client1.url, "https://config.dgtera.com")
                self.assertEqual(client1.db, "config_db")
                self.assertEqual(client1.username, "config_user")
                self.assertEqual(client1.password, "config_password")
            
            # Create client from test profile
            with patch('xmlrpc.client.ServerProxy'):  # Mock ServerProxy to avoid actual connections
                client2 = DgtClient.from_config(config_file=temp_path, profile="test")
                
                # Check that the client was configured correctly
                self.assertEqual(client2.url, "https://test-config.dgtera.com")
                self.assertEqual(client2.db, "test_config_db")
                self.assertEqual(client2.api_key, "test_config_api_key")
        
        finally:
            # Clean up the temporary file
            os.unlink(temp_path)

    def test_connection_error(self):
        """Test handling of connection errors."""
        # Mock a connection error
        self.common_mock.authenticate.side_effect = xmlrpc.client.ProtocolError(
            'https://test.dgtera.com', 500, 'Internal Server Error', {}
        )
        
        # Check that the error is properly wrapped in DgtException
        with self.assertRaises(DgtException) as context:
            self.client.authenticate()
        
        # Check the exception message
        self.assertIn("Protocol error", str(context.exception))

    def test_authentication_error(self):
        """Test handling of authentication errors."""
        # Mock an authentication error
        self.common_mock.authenticate.return_value = False
        
        # Check that the error is properly handled
        with self.assertRaises(DgtException) as context:
            self.client.authenticate()
        
        # Check the exception message
        self.assertIn("Authentication failed", str(context.exception))


if __name__ == '__main__':
    unittest.main() 