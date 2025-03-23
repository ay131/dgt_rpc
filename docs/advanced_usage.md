# Advanced Usage

This document covers advanced usage patterns and techniques for the DGT RPC Client.

## Custom Model Methods

The DGT RPC Client allows you to call any method on any model in your DgteraERP system.

### Basic Method Execution

```python
# Call a method with positional arguments
result = client.execute(
    model='product.product',
    method='get_product_multiline_description_sale',
    [product_id]
)

# Call a method with keyword arguments
result = client.execute_kw(
    model='product.product',
    method='name_search',
    args=[],
    kwargs={
        'name': 'Chair',
        'limit': 10
    }
)
```

### Working with Workflows

```python
# Confirm a sales order
client.execute(
    model='sale.order',
    method='action_confirm',
    [order_id]
)

# Validate an invoice
client.execute(
    model='account.move',
    method='action_post',
    [invoice_id]
)
```

## Batch Operations

For better performance when working with many records, use batch operations.

### Batch Creation

```python
# Create multiple products efficiently
products_to_create = [
    {'name': 'Product A', 'list_price': 10.0},
    {'name': 'Product B', 'list_price': 20.0},
    {'name': 'Product C', 'list_price': 30.0},
    # ... more products
]

product_ids = client.create_batch(
    model='product.product',
    values_list=products_to_create,
    batch_size=100  # Process 100 records at a time
)
```

### Batch Updates

```python
# Update multiple records efficiently
def update_products_in_batches(client, product_ids, new_price):
    batch_size = 100
    for i in range(0, len(product_ids), batch_size):
        batch = product_ids[i:i+batch_size]
        client.write(
            model='product.product',
            ids=batch,
            values={'list_price': new_price}
        )
        print(f"Updated batch {i//batch_size + 1}")

# Usage
update_products_in_batches(client, all_product_ids, 99.99)
```

## Working with Binary Fields

### Uploading Files

```python
import base64

# Read a file and encode it
with open('product_image.jpg', 'rb') as f:
    image_data = base64.b64encode(f.read()).decode('utf-8')

# Update a product with the image
client.write(
    model='product.product',
    ids=[product_id],
    values={'image_1920': image_data}
)
```

### Downloading Files

```python
import base64

# Get a binary field
attachment = client.search_read(
    model='ir.attachment',
    domain=[('id', '=', attachment_id)],
    fields=['name', 'datas']
)[0]

# Decode and save the file
file_data = base64.b64decode(attachment['datas'])
with open(attachment['name'], 'wb') as f:
    f.write(file_data)
```

## Advanced Querying

### Complex Domains

```python
# Find products that match complex criteria
domain = [
    '&',  # AND
    ('type', '=', 'product'),  # Storable products
    '|',  # OR
    ('qty_available', '<', 10),  # Low stock
    '&',  # AND
    ('categ_id.name', 'ilike', 'furniture'),  # In furniture category
    ('list_price', '>', 100)  # Expensive
]

products = client.search_read(
    model='product.product',
    domain=domain,
    fields=['name', 'qty_available', 'list_price']
)
```

### Pagination

```python
def get_all_records(client, model, domain=None, fields=None, batch_size=100):
    """Fetch all records matching the domain in batches."""
    domain = domain or []
    fields = fields or []
    offset = 0
    all_records = []
    
    while True:
        records = client.search_read(
            model=model,
            domain=domain,
            fields=fields,
            offset=offset,
            limit=batch_size
        )
        
        if not records:
            break
            
        all_records.extend(records)
        offset += batch_size
        print(f"Fetched {len(all_records)} records so far...")
        
    return all_records

# Usage
all_partners = get_all_records(
    client,
    model='res.partner',
    domain=[('customer_rank', '>', 0)],
    fields=['name', 'email', 'phone']
)
```

## Working with Relations

### Many2one Fields

```python
# Create a record with a many2one relation
lead_id = client.create(
    model='crm.lead',
    values={
        'name': 'New Lead',
        'partner_id': customer_id,  # many2one field
        'user_id': salesperson_id,  # many2one field
    }
)
```

### One2many Fields

```python
# Create a record with one2many lines
order_id = client.create(
    model='sale.order',
    values={
        'partner_id': customer_id,
        'order_line': [
            (0, 0, {  # (0, 0, values) creates a new line
                'product_id': product1_id,
                'product_uom_qty': 2,
            }),
            (0, 0, {
                'product_id': product2_id,
                'product_uom_qty': 1,
            })
        ]
    }
)
```

### Many2many Fields

```python
# Add tags to a partner (many2many)
client.write(
    model='res.partner',
    ids=[partner_id],
    values={
        'category_id': [
            (4, tag1_id),  # (4, id) adds a relation
            (4, tag2_id)
        ]
    }
)

# Replace all tags
client.write(
    model='res.partner',
    ids=[partner_id],
    values={
        'category_id': [(6, 0, [tag1_id, tag2_id])]  # (6, 0, [ids]) replaces all
    }
)

# Remove a tag
client.write(
    model='res.partner',
    ids=[partner_id],
    values={
        'category_id': [(3, tag1_id)]  # (3, id) removes a relation
    }
)
```

## Performance Optimization

### Selecting Specific Fields

```python
# Only request the fields you need
partners = client.search_read(
    model='res.partner',
    domain=[('customer_rank', '>', 0)],
    fields=['id', 'name', 'email']  # Only these fields will be fetched
)
```

### Using Raw XML-RPC

For maximum performance in specific cases, you can use the underlying XML-RPC connection directly:

```python
# Get the XML-RPC connection
common = client._get_common_connection()
models = client._get_models_connection()

# Use it directly
uid = common.authenticate(client.db, client.username, client.password, {})
result = models.execute_kw(client.db, uid, client.password, 
                          'res.partner', 'search_read', 
                          [[('customer_rank', '>', 0)]], 
                          {'fields': ['name', 'email'], 'limit': 5})
```

### Connection Pooling

For applications that need to handle multiple concurrent requests:

```python
from dgt_rpc import DgtClient
import concurrent.futures

# Create a connection pool
clients = [
    DgtClient(url="https://your-dgtera-instance.com", db="your_database", api_key="your_api_key")
    for _ in range(5)  # Create 5 client instances
]

# Authenticate all clients
for client in clients:
    client.authenticate()

# Function to process a batch of records
def process_batch(client, batch_ids):
    results = []
    for record_id in batch_ids:
        # Do something with each record
        record = client.read('product.product', [record_id], ['name', 'list_price'])[0]
        results.append(record)
    return results

# Get all product IDs
all_product_ids = clients[0].search('product.product', [])

# Split into batches
batch_size = len(all_product_ids) // len(clients)
batches = [all_product_ids[i:i+batch_size] for i in range(0, len(all_product_ids), batch_size)]

# Process in parallel
with concurrent.futures.ThreadPoolExecutor(max_workers=len(clients)) as executor:
    futures = [executor.submit(process_batch, clients[i], batch) 
               for i, batch in enumerate(batches)]
    
    all_results = []
    for future in concurrent.futures.as_completed(futures):
        all_results.extend(future.result())
```

## Error Handling and Retries

### Custom Retry Logic

```python
from dgt_rpc import DgtClient, DgtException
import time

def execute_with_retry(client, model, method, *args, max_retries=3, retry_delay=1):
    """Execute a method with custom retry logic."""
    for attempt in range(max_retries):
        try:
            return client.execute(model, method, *args)
        except DgtException as e:
            if "concurrency" in str(e).lower() and attempt < max_retries - 1:
                # This might be a concurrency error, retry after delay
                print(f"Concurrency error detected, retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
                continue
            else:
                # Re-raise the exception for other errors or if max retries reached
                raise

# Usage
try:
    result = execute_with_retry(
        client, 
        'sale.order', 
        'action_confirm', 
        [order_id],
        max_retries=5,
        retry_delay=2
    )
    print("Order confirmed successfully")
except DgtException as e:
    print(f"Failed to confirm order after retries: {e}")
```

## Working with Reports and Documents

### Generating Reports

```python
# Generate a PDF invoice
pdf_data = client.execute(
    model='ir.actions.report',
    method='render_qweb_pdf',
    [client.ref('account.account_invoices'), [invoice_id]]
)

# Save the PDF
with open('invoice.pdf', 'wb') as f:
    f.write(pdf_data[0])
```

### Creating Attachments

```python
import base64

# Read a file
with open('document.pdf', 'rb') as f:
    file_data = base64.b64encode(f.read()).decode('utf-8')

# Create an attachment
attachment_id = client.create(
    model='ir.attachment',
    values={
        'name': 'Document.pdf',
        'type': 'binary',
        'datas': file_data,
        'res_model': 'res.partner',
        'res_id': partner_id,
    }
)
```

## Advanced POS Operations

### Analyzing POS Data

```python
from dgt_rpc import DgtPOSClient
from datetime import datetime, timedelta

# Create a POS client
pos_client = DgtPOSClient(
    url="https://admin-instance.dgtera.com",
    db="admin_db",
    api_key="admin_api_key"
)

# Get all POS configurations
pos_configs = pos_client.get_pos_data("retail_db")

# Analyze sales by POS
pos_sales = {}
for pos_config in pos_configs:
    pos_id = pos_config['id']
    pos_name = pos_config['pos_name']
    
    # Get orders for this POS
    orders = pos_client.get_pos_orders(pos_id, "retail_db", limit=1000)
    
    # Calculate total sales
    total_sales = sum(order['amount_total'] for order in orders['all'])
    
    # Calculate average order value
    avg_order = total_sales / len(orders['all']) if orders['all'] else 0
    
    # Find top selling products
    product_sales = {}
    for order in orders['all']:
        for line in order['lines']:
            product_id = line['product_id'][0]
            product_name = line['product_id'][1]
            qty = line['qty']
            
            if product_id not in product_sales:
                product_sales[product_id] = {'name': product_name, 'qty': 0}
            
            product_sales[product_id]['qty'] += qty
    
    # Sort by quantity sold
    top_products = sorted(product_sales.items(), key=lambda x: x[1]['qty'], reverse=True)[:5]
    
    # Store results
    pos_sales[pos_id] = {
        'name': pos_name,
        'total_sales': total_sales,
        'avg_order': avg_order,
        'order_count': len(orders['all']),
        'top_products': top_products
    }

# Display results
for pos_id, data in pos_sales.items():
    print(f"\nPOS: {data['name']}")
    print(f"Total Sales: ${data['total_sales']:.2f}")
    print(f"Average Order: ${data['avg_order']:.2f}")
    print(f"Order Count: {data['order_count']}")
    
    print("Top Products:")
    for i, (product_id, product_data) in enumerate(data['top_products'], 1):
        print(f"  {i}. {product_data['name']} - {product_data['qty']} units")
```

## Conclusion

These advanced techniques should help you build more sophisticated applications with the DGT RPC Client. For specific use cases or further assistance, refer to the [API Reference](api_reference.md) or contact support.
