"""
MIT License

Copyright (c) 2023 DGTera

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import xmlrpc.client
import logging
import os
import configparser
from .exceptions import DgtException

logger = logging.getLogger(__name__)

class DgteraClient:
    """
    A generic client for interacting with Odoo instances via XML-RPC.
    
    This client provides methods to authenticate with an Odoo server,
    execute model methods, and perform common operations.
    """
    
    def __init__(self, url, db=None, username=None, password=None, api_key=None, timeout=120, max_retries=3, retry_delay=1):
        """
        Initialize the Odoo client.
        
        Args:
            url (str): The base URL of the Odoo instance (e.g., 'https://example.odoo.com')
            db (str, optional): The database name
            username (str, optional): The username for authentication
            password (str, optional): The password for authentication
            api_key (str, optional): API key for authentication (alternative to username/password)
            timeout (int, optional): Connection timeout in seconds
            max_retries (int, optional): Maximum number of retries for failed requests
            retry_delay (int, optional): Delay between retries in seconds
        """
        self.url = url.rstrip('/')
        self.db = db
        self.username = username
        self.password = password
        self.api_key = api_key
        self.uid = None
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.uid_cache = {}
        
    def _get_common_connection(self):
        """Get connection to the common endpoint."""
        return xmlrpc.client.ServerProxy(f'{self.url}/xmlrpc/2/common', timeout=self.timeout)
        
    def _get_models_connection(self):
        """Get connection to the models endpoint."""
        return xmlrpc.client.ServerProxy(f'{self.url}/xmlrpc/2/object', timeout=self.timeout)
        
    def authenticate(self, db=None, username=None, password=None, api_key=None, context=None):
        """
        Authenticate with the Odoo server.
        
        Args:
            db (str, optional): Database name (overrides instance attribute)
            username (str, optional): Username (overrides instance attribute)
            password (str, optional): Password (overrides instance attribute)
            api_key (str, optional): API key (overrides instance attribute)
            context (dict, optional): Additional context for authentication
            
        Returns:
            int: User ID if authentication successful
            
        Raises:
            DgtException: If authentication fails
        """
        db = db or self.db
        context = context or {}
        
        try:
            common = self._get_common_connection()
            
            # Check if we're using API key authentication
            if api_key or self.api_key:
                key = api_key or self.api_key
                cache_key = (db, key)
                
                if cache_key in self.uid_cache:
                    logger.debug("Using cached UID for API key authentication")
                    self.uid = self.uid_cache[cache_key]
                    return self.uid
                    
                uid = common.authenticate(db, 'admin', key, context)
                
            # Otherwise use username/password authentication
            else:
                username = username or self.username
                password = password or self.password
                cache_key = (db, username, password)
                
                if cache_key in self.uid_cache:
                    logger.debug("Using cached UID for username/password authentication")
                    self.uid = self.uid_cache[cache_key]
                    return self.uid
                    
                uid = common.authenticate(db, username, password, context)
            
            if not uid:
                raise DgtException("Authentication failed")
                
            logger.debug(f"Successfully authenticated, UID: {uid}")
            self.uid_cache[cache_key] = uid
            self.uid = uid
            return uid
            
        except xmlrpc.client.Error as e:
            raise DgtException.from_xmlrpc_exception(e)
        except Exception as e:
            raise DgtException(f"Authentication error", e)
    
    def execute(self, model, method, args=None, **kwargs):
        """
        Execute a method on an Odoo model.
        
        Args:
            model (str): The model name (e.g., 'res.partner')
            method (str): The method to call (e.g., 'search', 'read', 'write')
            args (list, optional): Positional arguments to pass to the method
            **kwargs: Additional parameters for the method
                
        Returns:
            The result of the method call
            
        Raises:
            DgtException: If the execution fails
        """
        if args is None:
            args = []
            
        try:
            models = self._get_models_connection()
            
            if not self.uid:
                self.authenticate()
                
            return models.execute_kw(
                self.db, self.uid, self.password or self.api_key,
                model, method, [args], kwargs
            )
        except xmlrpc.client.Error as e:
            raise DgtException.from_xmlrpc_exception(e)
        except Exception as e:
            raise DgtException(f"Error executing {method} on {model}", e)
    
    def execute_kw(self, model, method, args=None, kwargs=None):
        """
        Execute a method on an Odoo model with full control over arguments.
        
        Args:
            model (str): The model name
            method (str): The method to call
            args (list, optional): Positional arguments to pass to the method
            kwargs (dict, optional): Keyword arguments to pass to the method
                
        Returns:
            The result of the method call
            
        Raises:
            DgtException: If the execution fails
        """
        if args is None:
            args = []
        if kwargs is None:
            kwargs = {}
            
        try:
            models = self._get_models_connection()
            
            if not self.uid:
                self.authenticate()
                
            return models.execute_kw(
                self.db, self.uid, self.password or self.api_key,
                model, method, args, kwargs
            )
        except xmlrpc.client.Error as e:
            raise DgtException.from_xmlrpc_exception(e)
        except Exception as e:
            raise DgtException(f"Error executing {method} on {model}", e)
    
    def search(self, model, domain, offset=0, limit=None, order=None):
        """
        Search for records of a model.
        
        Args:
            model (str): The model name
            domain (list): The search domain
            offset (int, optional): Number of records to skip
            limit (int, optional): Maximum number of records to return
            order (str, optional): Field(s) to sort by
            
        Returns:
            list: Record IDs matching the domain
            
        Raises:
            DgtException: If the search fails
        """
        kwargs = {
            'offset': offset,
            'limit': limit,
            'order': order
        }
        return self.execute_kw(model, 'search', [[domain]], kwargs)
    
    def read(self, model, ids, fields=None):
        """
        Read records of a model.
        
        Args:
            model (str): The model name
            ids (list): List of record IDs to read
            fields (list, optional): List of fields to read, reads all if not specified
            
        Returns:
            list: List of dictionaries containing the read data
            
        Raises:
            DgtException: If the read fails
        """
        kwargs = {}
        if fields:
            kwargs['fields'] = fields
        return self.execute_kw(model, 'read', [[ids]], kwargs)
    
    def search_read(self, model, domain, fields=None, offset=0, limit=None, order=None):
        """
        Search and read records in a single call.
        
        Args:
            model (str): The model name
            domain (list): The search domain
            fields (list, optional): List of fields to read
            offset (int, optional): Number of records to skip
            limit (int, optional): Maximum number of records to return
            order (str, optional): Field(s) to sort by
            
        Returns:
            list: List of dictionaries containing the read data
            
        Raises:
            DgtException: If the search_read fails
        """
        kwargs = {
            'offset': offset,
            'limit': limit,
            'order': order
        }
        if fields:
            kwargs['fields'] = fields
        return self.execute_kw(model, 'search_read', [[domain]], kwargs)
    
    def create(self, model, values):
        """
        Create a new record.
        
        Args:
            model (str): The model name
            values (dict): Field values for the new record
            
        Returns:
            int: ID of the created record
            
        Raises:
            DgtException: If the creation fails
        """
        return self.execute_kw(model, 'create', [[values]])
    
    def write(self, model, ids, values):
        """
        Update existing records.
        
        Args:
            model (str): The model name
            ids (list): List of record IDs to update
            values (dict): Field values to update
            
        Returns:
            bool: True if successful
            
        Raises:
            DgtException: If the update fails
        """
        return self.execute_kw(model, 'write', [[ids, values]])
    
    def unlink(self, model, ids):
        """
        Delete records.
        
        Args:
            model (str): The model name
            ids (list): List of record IDs to delete
            
        Returns:
            bool: True if successful
            
        Raises:
            DgtException: If the deletion fails
        """
        return self.execute_kw(model, 'unlink', [[ids]])
        
    def create_batch(self, model, values_list, batch_size=100):
        """
        Create multiple records in batches.
        
        Args:
            model (str): The model name
            values_list (list): List of dictionaries with field values
            batch_size (int, optional): Number of records to create in each batch
            
        Returns:
            list: List of created record IDs
            
        Raises:
            DgtException: If any batch creation fails
        """
        result = []
        
        for i in range(0, len(values_list), batch_size):
            batch = values_list[i:i+batch_size]
            batch_result = self.execute_kw(model, 'create', [batch])
            result.extend(batch_result)
            
        return result
        
    @classmethod
    def from_environment(cls, **kwargs):
        """
        Create a client from environment variables.
        
        Environment variables:
            DGTERA_URL: The Odoo URL
            DGTERA_DB: The database name
            DGTERA_USERNAME: The username
            DGTERA_PASSWORD: The password
            DGTERA_API_KEY: The API key
            DGTERA_TIMEOUT: Connection timeout in seconds
            DGTERA_MAX_RETRIES: Maximum number of retries
            DGTERA_RETRY_DELAY: Delay between retries in seconds
            
        Args:
            **kwargs: Override environment variables
            
        Returns:
            DgteraClient: A new client instance
        """
        config = {
            'url': os.environ.get('DGTERA_URL'),
            'db': os.environ.get('DGTERA_DB'),
            'username': os.environ.get('DGTERA_USERNAME'),
            'password': os.environ.get('DGTERA_PASSWORD'),
            'api_key': os.environ.get('DGTERA_API_KEY'),
        }
        
        # Parse numeric settings
        if 'DGTERA_TIMEOUT' in os.environ:
            config['timeout'] = int(os.environ.get('DGTERA_TIMEOUT'))
        if 'DGTERA_MAX_RETRIES' in os.environ:
            config['max_retries'] = int(os.environ.get('DGTERA_MAX_RETRIES'))
        if 'DGTERA_RETRY_DELAY' in os.environ:
            config['retry_delay'] = int(os.environ.get('DGTERA_RETRY_DELAY'))
            
        # Override with kwargs
        config.update({k: v for k, v in kwargs.items() if v is not None})
        
        # Remove None values
        config = {k: v for k, v in config.items() if v is not None}
        
        return cls(**config)
        
    @classmethod
    def from_config(cls, config_file='~/.dgtera.cfg', profile='default', **kwargs):
        """
        Create a client from a configuration file.
        
        Args:
            config_file (str): Path to the configuration file
            profile (str): Configuration profile to use
            **kwargs: Override configuration file settings
            
        Returns:
            DgteraClient: A new client instance
        """
        config_file = os.path.expanduser(config_file)
        
        if not os.path.exists(config_file):
            raise DgtException(f"Configuration file not found: {config_file}")
            
        parser = configparser.ConfigParser()
        parser.read(config_file)
        
        if profile not in parser:
            raise DgtException(f"Profile '{profile}' not found in {config_file}")
            
        section = parser[profile]
        
        config = {
            'url': section.get('url'),
            'db': section.get('db'),
            'username': section.get('username'),
            'password': section.get('password'),
            'api_key': section.get('api_key'),
        }
        
        # Parse numeric settings
        if 'timeout' in section:
            config['timeout'] = section.getint('timeout')
        if 'max_retries' in section:
            config['max_retries'] = section.getint('max_retries')
        if 'retry_delay' in section:
            config['retry_delay'] = section.getint('retry_delay')
            
        # Override with kwargs
        config.update({k: v for k, v in kwargs.items() if v is not None})
        
        # Remove None values
        config = {k: v for k, v in config.items() if v is not None}
        
        return cls(**config)


class DgteraPOSClient(DgteraClient):
    """
    A specialized client for working with Odoo POS systems.
    
    This extends the generic Dgtera Client with methods specific to POS operations.
    """
    
    def get_pos_data(self, db, include_inactive=True):
        """
        Get POS configuration data.
        
        Args:
            db (str): The database to get POS data for
            include_inactive (bool, optional): Whether to include inactive POS configs
            
        Returns:
            list: List of POS configurations
            
        Raises:
            DgtException: If the operation fails
        """
        return self.execute_kw("pos.config", "get_pos_data", [db, include_inactive])
    
    def get_pos_orders(self, pos_config, db, limit=10, include_lines=False):
        """
        Get orders for a POS configuration.
        
        Args:
            pos_config (dict or int): POS configuration dictionary or ID
            db (str): The database name
            limit (int, optional): Maximum number of orders to retrieve
            include_lines (bool, optional): Whether to include order lines
            
        Returns:
            dict: Dictionary with order data
            
        Raises:
            DgtException: If the operation fails
        """
        # If pos_config is a dictionary, extract the ID
        pos_id = pos_config.get('id') if isinstance(pos_config, dict) else pos_config
        
        return self.execute_kw("pos.order", "get_pos_orders", [pos_id, db, limit, include_lines])


# Example usage
if __name__ == "__main__":
    import sys
    
    # Set up logging
    logging.basicConfig(level=logging.INFO, 
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Get inputs
    db_name = input("Enter database name: ")
    base_url = input("Enter base URL: ")
    base_db = input("Enter admin database name: ")
    base_api_key = input("Enter admin API key: ")
    
    # Create client
    client = DgteraPOSClient(base_url, base_db, api_key=base_api_key)
    
    # Authenticate
    uid = client.authenticate()
    if not uid:
        print("Authentication failed. Exiting.")
        sys.exit(1)
        
    # Get POS data
    pos_configs = client.get_pos_data(db_name)
    if not pos_configs:
        print("No POS configurations found.")
        sys.exit(0)
        
    # Print POS data
    print("\nExtracted POS Configurations:")
    print("-" * 80)
    print(f"{'POS ID':<8} {'POS Name':<15} {'Database':<10} {'PIN':<18} {'Username':<12} {'URL':<30} {'API Key'}")
    print("-" * 80)
    
    for item in pos_configs:
        print(f"{item.get('pos_ID', ''):<8} {item.get('pos_name', ''):<15} {item.get('database', ''):<10} "
              f"{item.get('pin', ''):<18} {item.get('username', ''):<12} {item.get('url', ''):<30} "
              f"{item.get('api_key', '')}")
    print("-" * 80)
    
    # Get orders for each POS
    for pos_config in pos_configs:
        try:
            orders = client.get_pos_orders(pos_config, db_name)
            
            print(f"\nOrders for POS: {pos_config.get('pos_name')} (ID: {pos_config.get('pos_ID')})")
            print("-" * 80)
            print(f"{'Type':<10} {'Order Name':<15} {'Date':<25} {'iOS Version':<15} {'Config ID'}")
            print("-" * 80)
            
            if 'oldest' in orders and orders['oldest']:
                for order in orders['oldest']:
                    config_id = order.get('config_id')
                    if isinstance(config_id, list) and len(config_id) > 1:
                        config_id = config_id[0]
                    print(f"{'Oldest':<10} {order.get('name', ''):<15} {order.get('date_order', ''):<25} "
                          f"{order.get('ios_version', ''):<15} {config_id}")
                          
            if 'newest' in orders and orders['newest']:
                for order in orders['newest']:
                    config_id = order.get('config_id')
                    if isinstance(config_id, list) and len(config_id) > 1:
                        config_id = config_id[0]
                    print(f"{'Newest':<10} {order.get('name', ''):<15} {order.get('date_order', ''):<25} "
                          f"{order.get('ios_version', ''):<15} {config_id}")
                          
            print("-" * 80)
            
        except Exception as e:
            print(f"Error processing orders for POS {pos_config.get('pos_name')}: {e}")
