import xmlrpc.client

class OdooXMLRPC:
    def __init__(self, db_name,base_api_key):
        self.base_url="https://erp.dgtera.com"
        self.base_api_key = base_api_key
        self.base_db = 'erp'
        self.db_name = db_name
        self.common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(self.base_url))
        self.uid_cache = {}

    def authenticate(self, db, api_key):
        if (db, api_key) in self.uid_cache:
            print("Using cached UID.")
            return self.uid_cache[(db, api_key)]
        uid = self.common.authenticate(db, 'api_key_user', api_key, {})
        if not uid:
            print("Authentication failed.")
            return None
        self.uid_cache[(db, api_key)] = uid
        print("Successfully authenticated, UID:", uid)
        return uid

    def get_data(self, db, uid):
        models = xmlrpc.client.ServerProxy(f'{self.base_url}/xmlrpc/2/object')
        result = models.execute_kw(self.base_db, uid, self.base_api_key, 'dgt.ios.admin', 'get_data_by_db', [db])
        if result:
            print("\nExtracted Data:")
            print("-" * 80)
            print(
                f"{'POS ID':<8} {'POS Name':<15} {'Database':<10} {'PIN':<25} {'username':<25} {'URL':<25} {'api_key':<80}")
            print("-" * 80)

            for item in result:
                print(f"{item.get('pos_ID', ''):<8} {item.get('pos_name', ''):<15} {item.get('database', ''):<10} "
                      f"{item.get('pin', ''):<25} {item.get('username', ''):<25} {item.get('url', '')} "
                      f" {item.get('api_key', ''):<80}")
            print("-" * 80)
        else:
            print("No data found.")
        return result

    def get_orders(self, db, res):
        if res.get('pos_type') == 'pos':
            common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(res.get("url")))
            uid = common.authenticate(db, res.get("username"), res.get("api_key"), {})
            models = xmlrpc.client.ServerProxy(f'{res.get("url")}/xmlrpc/2/object')
            fields = ['date_order', 'name', 'ios_version', 'config_id']  # Specify only necessary fields
            oldest_order_ids = models.execute_kw(db, uid, res.get('api_key'), 'pos.order', 'search', 
                                                [[['id', '!=', False], ['config_id', '=', res.get('pos_ID')]]],
                                                {'order': 'date_order asc', 'limit': 1})
            newest_order_ids = models.execute_kw(db, uid, res.get('api_key'), 'pos.order', 'search', 
                                                [[['id', '!=', False], ['config_id', '=', res.get('pos_ID')]]],
                                                {'order': 'date_order desc', 'limit': 1})
            
            print(f"\nOrders for POS: {res.get('pos_name')} (ID: {res.get('pos_ID')})")
            print("-" * 80)
            # if not oldest_order_ids and not newest_order_ids:
            #     print("No orders found.")
            #     return
            print(f"{'Type':<10} {'Order Name':<15} {'Date':<25} {'iOS Version':<15} {'Config ID'}")
            print("-" * 80)
            
            if oldest_order_ids:
                oldest_order = models.execute_kw(db, uid, res.get('api_key'), 'pos.order', 'read', [oldest_order_ids],
                                                {'fields': fields})
                for order in oldest_order:
                    print(f"{'Oldest':<10} {order.get('name', ''):<15} {order.get('date_order', ''):<25} "
                          f"{order.get('ios_version', ''):<15} {order.get('config_id')[0] if isinstance(order.get('config_id'), list) else order.get('config_id', '')}")
            
            if newest_order_ids:
                newest_order = models.execute_kw(db, uid, res.get('api_key'), 'pos.order', 'read', [newest_order_ids],
                                                {'fields': fields})
                for order in newest_order:
                    print(f"{'Newest':<10} {order.get('name', ''):<15} {order.get('date_order', ''):<25} "
                          f"{order.get('ios_version', ''):<15} {order.get('config_id')[0] if isinstance(order.get('config_id'), list) else order.get('config_id', '')}")
            
            print("-" * 80)

if __name__ == "__main__":
    db_name = input("Enter database name: ")
    base_api_key = input("Enter API key: ") #gKMFln1avBnYapGmD0cWNTub0MypgPFWRJGmLRbTxe2V8sCMIp0YrYBTYtWGKBmd3DXWAQMobQqtReqb0TZsdg

    odoo_rpc = OdooXMLRPC(db_name, base_api_key)
    uid = odoo_rpc.authenticate(odoo_rpc.base_db, odoo_rpc.base_api_key)
    if uid:
        result = odoo_rpc.get_data(db_name, uid)
        for res in result:
            try:
                odoo_rpc.get_orders(db_name, res)
            except Exception as e:
                print(f"Error: {e}")
