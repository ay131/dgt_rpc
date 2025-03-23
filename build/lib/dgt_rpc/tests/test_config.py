import unittest
from unittest.mock import patch, mock_open
import os
import tempfile

from dgt_rpc import DgtClient

class TestConfiguration(unittest.TestCase):
    """Test cases for configuration loading."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        # Save original environment variables
        self.original_env = os.environ.copy()

    def tearDown(self):
        """Clean up after each test method."""
        # Restore original environment variables
        os.environ.clear()
        os.environ.update(self.original_env)

    def test_environment_variables_full(self):
        """Test loading all configuration from environment variables."""
        # Set all environment variables
        os.environ['DGTERA_URL'] = "https://env.dgtera.com"
        os.environ['DGTERA_DB'] = "env_db"
        os.environ['DGTERA_USERNAME'] = "env_user"
        os.environ['DGTERA_PASSWORD'] = "env_password"
        os.environ['DGTERA_TIMEOUT'] = "60"
        os.environ['DGTERA_MAX_RETRIES'] = "5"
        os.environ['DGTERA_RETRY_DELAY'] = "2"
        
        # Create client from environment
        with patch('xmlrpc.client.ServerProxy'):  # Mock ServerProxy to avoid actual connections
            client = DgtClient.from_environment()
            
            # Check that all settings were loaded correctly
            self.assertEqual(client.url, "https://env.dgtera.com")
            self.assertEqual(client.db, "env_db")
            self.assertEqual(client.username, "env_user")
            self.assertEqual(client.password, "env_password")
            self.assertEqual(client.timeout, 60)
            self.assertEqual(client.max_retries, 5)
            self.assertEqual(client.retry_delay, 2)

    def test_environment_variables_api_key(self):
        """Test loading configuration with API key from environment variables."""
        # Set environment variables with API key
        os.environ['DGTERA_URL'] = "https://env.dgtera.com"
        os.environ['DGTERA_DB'] = "env_db"
        os.environ['DGTERA_API_KEY'] = "env_api_key"
        
        # Create client from environment
        with patch('xmlrpc.client.ServerProxy'):  # Mock ServerProxy to avoid actual connections
            client = DgtClient.from_environment()
            
            # Check that settings were loaded correctly
            self.assertEqual(client.url, "https://env.dgtera.com")
            self.assertEqual(client.db, "env_db")
            self.assertEqual(client.api_key, "env_api_key")
            self.assertIsNone(client.username)
            self.assertIsNone(client.password)

    def test_environment_variables_partial(self):
        """Test loading partial configuration from environment variables."""
        # Set only some environment variables
        os.environ['DGTERA_URL'] = "https://env.dgtera.com"
        
        # Create client from environment with some direct parameters
        with patch('xmlrpc.client.ServerProxy'):  # Mock ServerProxy to avoid actual connections
            client = DgtClient.from_environment(db="direct_db", username="direct_user", password="direct_pass")
            
            # Check that settings were merged correctly
            self.assertEqual(client.url, "https://env.dgtera.com")  # From environment
            self.assertEqual(client.db, "direct_db")  # From direct parameters
            self.assertEqual(client.username, "direct_user")  # From direct parameters
            self.assertEqual(client.password, "direct_pass")  # From direct parameters

    def test_config_file_default_profile(self):
        """Test loading configuration from a file with default profile."""
        # Create a temporary config file
        config_content = """
        [default]
        url = https://config.dgtera.com
        db = config_db
        username = config_user
        password = config_password
        timeout = 90
        max_retries = 4
        retry_delay = 3
        """
        
        with tempfile.NamedTemporaryFile(mode='w+', delete=False) as temp:
            temp.write(config_content)
            temp_path = temp.name
        
        try:
            # Create client from config file
            with patch('xmlrpc.client.ServerProxy'):  # Mock ServerProxy to avoid actual connections
                client = DgtClient.from_config(config_file=temp_path)
                
                # Check that settings were loaded correctly
                self.assertEqual(client.url, "https://config.dgtera.com")
                self.assertEqual(client.db, "config_db")
                self.assertEqual(client.username, "config_user")
                self.assertEqual(client.password, "config_password")
                self.assertEqual(client.timeout, 90)
                self.assertEqual(client.max_retries, 4)
                self.assertEqual(client.retry_delay, 3)
        
        finally:
            # Clean up the temporary file
            os.unlink(temp_path)

    def test_config_file_specific_profile(self):
        """Test loading configuration from a file with a specific profile."""
        # Create a temporary config file with multiple profiles
        config_content = """
        [default]
        url = https://default.dgtera.com
        db = default_db
        
        [production]
        url = https://prod.dgtera.com
        db = prod_db
        api_key = prod_api_key
        timeout = 180
        
        [development]
        url = https://dev.dgtera.com
        db = dev_db
        username = dev_user
        password = dev_pass
        """
        
        with tempfile.NamedTemporaryFile(mode='w+', delete=False) as temp:
            temp.write(config_content)
            temp_path = temp.name
        
        try:
            # Create client from production profile
            with patch('xmlrpc.client.ServerProxy'):  # Mock ServerProxy to avoid actual connections
                prod_client = DgtClient.from_config(config_file=temp_path, profile="production")
                
                # Check that settings were loaded correctly
                self.assertEqual(prod_client.url, "https://prod.dgtera.com")
                self.assertEqual(prod_client.db, "prod_db")
                self.assertEqual(prod_client.api_key, "prod_api_key")
                self.assertEqual(prod_client.timeout, 180)
            
            # Create client from development profile
            with patch('xmlrpc.client.ServerProxy'):  # Mock ServerProxy to avoid actual connections
                dev_client = DgtClient.from_config(config_file=temp_path, profile="development")
                
                # Check that settings were loaded correctly
                self.assertEqual(dev_client.url, "https://dev.dgtera.com")
                self.assertEqual(dev_client.db, "dev_db")
                self.assertEqual(dev_client.username, "dev_user")
                self.assertEqual(dev_client.password, "dev_pass")
        
        finally:
            # Clean up the temporary file
            os.unlink(temp_path)

    def test_config_file_override(self):
        """Test overriding config file settings with direct parameters."""
        # Create a temporary config file
        config_content = """
        [default]
        url = https://config.dgtera.com
        db = config_db
        username = config_user
        password = config_password
        """
        
        with tempfile.NamedTemporaryFile(mode='w+', delete=False) as temp:
            temp.write(config_content)
            temp_path = temp.name
        
        try:
            # Create client with some direct parameters that override the config
            with patch('xmlrpc.client.ServerProxy'):  # Mock ServerProxy to avoid actual connections
                client = DgtClient.from_config(
                    config_file=temp_path,
                    url="https://override.dgtera.com",
                    db="override_db"
                )
                
                # Check that settings were merged correctly
                self.assertEqual(client.url, "https://override.dgtera.com")  # From direct parameters
                self.assertEqual(client.db, "override_db")  # From direct parameters
                self.assertEqual(client.username, "config_user")  # From config file
                self.assertEqual(client.password, "config_password")  # From config file
        
        finally:
            # Clean up the temporary file
            os.unlink(temp_path)


if __name__ == '__main__':
    unittest.main() 