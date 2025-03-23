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

logger = logging.getLogger(__name__)

class OdooClient:
    """
    A generic client for interacting with Odoo instances via XML-RPC.
    
    This client provides methods to authenticate with an Odoo server,
    execute model methods, and perform common operations.
    """
    
    def __init__(self, url, db=None, username=None, password=None, api_key=None):
        """
        Initialize the Odoo client.
        
        Args:
            url (str): The base URL of the Odoo instance (e.g., 'https://example.odoo.com')
            db (str, optional): The database name
            username (str, optional): The username for authentication
            password (str, optional): The password for authentication
            api_key (str, optional): API key for authentication (alternative to username/password)
        """
        self.url = url.rstrip('/')
        self.db = db
        self.username = username
        self.password = password
        self.api_key = api_key
        self.uid = None
        self.common = xmlrpc.client.ServerProxy(f'{self.url}/xmlrpc/2/common')
        self.models = xmlrpc.client.ServerProxy(f'{self.url}/xmlrpc/2/object')
        self.uid_cache = {}
        
    def authenticate(self, db=None, username=None, password=None, api_key=None):
        """
        Authenticate with the Odoo server.
        
        Args:
            db (str, optional): Database name (overrides instance attribute)
            username (str, optional): Username (overrides instance attribute)
            password (str, optional): Password (overrides instance attribute)
            api_key (str, optional): API key (overrides instance attribute)
            
        Returns:
            int: User ID if authentication successful, None otherwise
        """
        db = db or self.db
        
        # Check if we're using API key authentication
        if api_key or self.api_key:
            key = api_key or self.api_key
            cache_key = (db, key)
            
            if cache_key in self.uid_cache:
                logger.debug("Using cached UID for API key authentication")
                self.uid = self.uid_cache[cache_key]
                return self.uid
                
            uid = self.common.authenticate(db, 'api_key_user', key, {})
            
        # Otherwise use username/password authentication
        else:
            username = username or self.username
            password = password or self.password
            cache_key = (db, username, password)
            
            if cache_key in self.uid_cache:
                logger.debug("Using cached UID for username/password authentication")
                self.uid = self.uid_cache[cache_key]
                return self.uid
                
            uid = self.common.authenticate(db, username, password, {})
        
        if not uid:
            logger.error("Authentication failed")
            return None
            
        logger.debug(f"Successfully authenticated, UID: {uid}")
        self.uid_cache[cache_key] = uid
        self.uid = uid
        return uid
    
    def execute(self, model, method, *args, **kwargs):
        """
        Execute a method on an Odoo model.
        
        Args:
            model (str): The model name (e.g., 'res.partner')
            method (str): The method to call (e.g., 'search', 'read', 'write')
            *args: Positional arguments to pass to the method
            **kwargs: Additional parameters:
                - db (str, optional): Database to use for this call
                - uid (int, optional): User ID to use for this call
                - password (str, optional): Password/API key to use for this call
                
        Returns:
            The result of the method call
        """
        db = kwargs.pop('db', self.db)
        uid = kwargs.pop('uid', self.uid)
        password = kwargs.pop('password', self.password or self.api_key)
        
        if not all([db, uid, password]):
            raise ValueError("Missing required authentication parameters. Call authenticate() first.")
        
        return self.models.execute_kw(db, uid, password, model, method, args, kwargs)
    
    def search(self, model, domain, **kwargs):
        """
        Search for records of a model.
        
        Args:
            model (str): The model name
            domain (list): The search domain
            **kwargs: Additional parameters like offset, limit, order
            
        Returns:
            list: Record IDs matching the domain
        """
        return self.execute(model, 'search', domain, kwargs)
    
    def read(self, model, ids, fields=None):
        """
        Read records of a model.
        
        Args:
            model (str): The model name
            ids (list): List of record IDs to read
            fields (list, optional): List of fields to read, reads all if not specified
            
        Returns:
            list: List of dictionaries containing the read data
        """
        kwargs = {}
        if fields:
            kwargs['fields'] = fields
        return self.execute(model, 'read', ids, kwargs)
    
    def search_read(self, model, domain, fields=None, **kwargs):
        """
        Search and read records in a single call.
        
        Args:
            model (str): The model name
            domain (list): The search domain
            fields (list, optional): List of fields to read
            **kwargs: Additional parameters like offset, limit, order
            
        Returns:
            list: List of dictionaries containing the read data
        """
        if fields:
            kwargs['fields'] = fields
        return self.execute(model, 'search_read', domain, kwargs)
    
    def create(self, model, values):
        """
        Create a new record.
        
        Args:
            model (str): The model name
            values (dict): Field values for the new record
            
        Returns:
            int: ID of the created record
        """
        return self.execute(model, 'create', values)
    
    def write(self, model, ids, values):
        """
        Update existing records.
        
        Args:
            model (str): The model name
            ids (list): List of record IDs to update
            values (dict): Field values to update
            
        Returns:
            bool: True if successful
        """
        return self.execute(model, 'write', ids, values)
    
    def unlink(self, model, ids):
        """
        Delete records.
        
        Args:
            model (str): The model name
            ids (list): List of record IDs to delete
            
        Returns:
            bool: True if successful
        """
        return self.execute(model, 'unlink', ids)


class OdooPOSClient(OdooClient):
    """
    A specialized client for working with Odoo POS systems.
    
    This extends the generic OdooClient with methods specific to POS operations.
    """
    
    def get_pos_data(self, db, admin_db=None, admin_api_key=None):
        """
        Get POS configuration data from an admin database.
        
        Args:
            db (str): The database to get POS data for
            admin_db (str, optional): The admin database name
            admin_api_key (str, optional): The admin API key
            
        Returns:
            list: List of POS configurations
        """
        admin_db = admin_db or self.db
        admin_api_key = admin_api_key or self.api_key
        
        if not self.uid:
            self.authenticate(admin_db, api_key=admin_api_key)
            
        return self.execute('dgt.ios.admin', 'get_data_by_db', db, 
                           db=admin_db, password=admin_api_key)
    
    def get_pos_orders(self, pos_config, db=None, limit_oldest=1, limit_newest=1):
        """
        Get the oldest and newest orders for a POS configuration.
        
        Args:
            pos_config (dict): POS configuration dictionary with keys:
                - pos_ID: The POS ID
                - url: The Odoo URL
                - username: The username
                - api_key: The API key
            db (str, optional): The database name
            limit_oldest (int, optional): Number of oldest orders to retrieve
            limit_newest (int, optional): Number of newest orders to retrieve
            
        Returns:
            dict: Dictionary with 'oldest' and 'newest' keys containing order data
        """
        db = db or self.db
        
        if pos_config.get('pos_type') != 'pos':
            return {}
            
        # Create a temporary client for this POS
        pos_client = OdooClient(
            url=pos_config.get('url'),
            db=db,
            username=pos_config.get('username'),
            api_key=pos_config.get('api_key')
        )
        
        uid = pos_client.authenticate()
        if not uid:
            logger.error(f"Failed to authenticate with POS {pos_config.get('pos_name')}")
            return {}
            
        fields = ['date_order', 'name', 'ios_version', 'config_id']
        domain = [['id', '!=', False], ['config_id', '=', pos_config.get('pos_ID')]]
        
        orders = {}
        
        # Get oldest orders
        if limit_oldest > 0:
            oldest_ids = pos_client.search('pos.order', domain, 
                                          order='date_order asc', limit=limit_oldest)
            if oldest_ids:
                orders['oldest'] = pos_client.read('pos.order', oldest_ids, fields)
                
        # Get newest orders
        if limit_newest > 0:
            newest_ids = pos_client.search('pos.order', domain, 
                                          order='date_order desc', limit=limit_newest)
            if newest_ids:
                orders['newest'] = pos_client.read('pos.order', newest_ids, fields)
                
        return orders


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
    client = OdooPOSClient(base_url, base_db, api_key=base_api_key)
    
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
