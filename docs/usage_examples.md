# Usage Examples

This document provides practical examples of using the DGT RPC Client in various scenarios.

## Table of Contents
- [Basic Operations](#basic-operations)
- [Working with Products](#working-with-products)
- [Customer Management](#customer-management)
- [Sales Order Processing](#sales-order-processing)
- [POS Operations](#pos-operations)
- [Reporting](#reporting)
- [Batch Processing](#batch-processing)

## Basic Operations

### Setting Up the Client

```python
from dgt_rpc import DgtClient

# Create and authenticate the client
client = DgtClient(
    url="https://your-dgtera-instance.com",
    db="your_database",
    api_key="your_api_key"
)

uid = client.authenticate()
if not uid:
    raise Exception("Authentication failed")
```

### Executing Custom Methods

```python
# Call a custom method on a model
result = client.execute(
    model='product.product',
    method='get_product_multiline_description_sale',
    [product_id]
)
```

### Searching Records

```python
# Search for products with stock less than 10
low_stock_products = client.search_read(
    model='product.product',
    domain=[('qty_available', '<', 10), ('type', '=', 'product')],
    fields=['name', 'qty_available', 'default_code'],
    order='qty_available'
)

for product in low_stock_products:
    print(f"Low stock: {product['name']} - {product['qty_available']} units available")
```

### Complex Domain Filters

```python
# Find invoices that are overdue but not sent to the customer
domain = [
    '&',
    ('invoice_date_due', '<', datetime.today().strftime('%Y-%m-%d')),
    '&',
    ('state', '=', 'posted'),
    ('is_move_sent', '=', False)
]

overdue_invoices = client.search_read(
    model='account.move',
    domain=domain,
    fields=['name', 'partner_id', 'amount_total', 'invoice_date_due']
)
```

## Working with Products

### Creating Products with Variants

```python
# Create a product template with attributes
template_id = client.create(
    model='product.template',
    values={
        'name': 'Configurable T-Shirt',
        'type': 'product',
        'list_price': 25.0,
    }
)

# Add size attribute
size_attr_id = client.create(
    model='product.attribute',
    values={'name': 'Size'}
)

# Add size values
size_values = [
    {'name': 'S'},
    {'name': 'M'},
    {'name': 'L'},
    {'name': 'XL'}
]
size_value_ids = []
for value in size_values:
    value['attribute_id'] = size_attr_id
    size_value_ids.append(client.create('product.attribute.value', value))

# Add color attribute
color_attr_id = client.create(
    model='product.attribute',
    values={'name': 'Color'}
)

# Add color values
color_values = [
    {'name': 'Red'},
    {'name': 'Blue'},
    {'name': 'Green'}
]
color_value_ids = []
for value in color_values:
    value['attribute_id'] = color_attr_id
    color_value_ids.append(client.create('product.attribute.value', value))

# Link attributes to template
client.create(
    model='product.template.attribute.line',
    values={
        'product_tmpl_id': template_id,
        'attribute_id': size_attr_id,
        'value_ids': [(6, 0, size_value_ids)]
    }
)

client.create(
    model='product.template.attribute.line',
    values={
        'product_tmpl_id': template_id,
        'attribute_id': color_attr_id,
        'value_ids': [(6, 0, color_value_ids)]
    }
)

# Get all variants created
variants = client.search_read(
    model='product.product',
    domain=[('product_tmpl_id', '=', template_id)],
    fields=['name', 'default_code']
)
print(f"Created {len(variants)} product variants")
```

### Updating Product Stock

```python
# Update stock quantity
inventory_adjustment = client.create(
    model='stock.quant',
    values={
        'product_id': product_id,
        'location_id': warehouse_location_id,
        'inventory_quantity': 100  # Set absolute quantity
    }
)

# Apply the inventory adjustment
client.execute(
    model='stock.quant',
    method='action_apply_inventory',
    [inventory_adjustment]
)
```

## Customer Management

### Creating a Customer with Contacts

```python
# Create a company
company_id = client.create(
    model='res.partner',
    values={
        'name': 'ABC Corporation',
        'is_company': True,
        'street': '123 Business Ave',
        'city': 'Enterprise City',
        'zip': '12345',
        'country_id': country_id,
        'email': 'info@abccorp.example',
        'phone': '+1 234 567 8900',
        'website': 'https://www.abccorp.example'
    }
)

# Create a contact under the company
contact_id = client.create(
    model='res.partner',
    values={
        'name': 'John Smith',
        'parent_id': company_id,
        'type': 'contact',
        'email': 'john.smith@abccorp.example',
        'phone': '+1 234 567 8901',
        'mobile': '+1 234 567 8902'
    }
)

# Add a shipping address
shipping_id = client.create(
    model='res.partner',
    values={
        'name': 'ABC Corp Warehouse',
        'parent_id': company_id,
        'type': 'delivery',
        'street': '789 Shipping Lane',
        'city': 'Logistics City',
        'zip': '54321',
        'country_id': country_id,
        'email': 'warehouse@abccorp.example',
        'phone': '+1 234 567 8903'
    }
)
```

## Sales Order Processing

### Creating and Confirming a Sales Order

```python
# Create a sales order
order_id = client.create(
    model='sale.order',
    values={
        'partner_id': customer_id,
        'partner_invoice_id': customer_id,
        'partner_shipping_id': shipping_address_id,
        'pricelist_id': pricelist_id,
        'payment_term_id': payment_term_id
    }
)

# Add order lines
for product in products_to_order:
    client.create(
        model='sale.order.line',
        values={
            'order_id': order_id,
            'product_id': product['id'],
            'product_uom_qty': product['quantity'],
            'price_unit': product.get('price', 0.0)
        }
    )

# Confirm the order
client.execute(
    model='sale.order',
    method='action_confirm',
    [order_id]
)

# Get the order status
order = client.read(
    model='sale.order',
    ids=[order_id],
    fields=['name', 'state', 'amount_total']
)[0]

print(f"Order {order['name']} confirmed with status {order['state']}")
print(f"Total amount: {order['amount_total']}")
```

## POS Operations

### Getting POS Configuration Data

```python
from dgt_rpc import DgtPOSClient

# Create a POS client
pos_client = DgtPOSClient(
    url="https://admin-instance.dgtera.com",
    db="admin_db",
    api_key="admin_api_key"
)

# Get POS configurations for a specific database
pos_configs = pos_client.get_pos_data("retail_db")

# Display POS configurations
for pos in pos_configs:
    print(f"POS: {pos.get('pos_name')}, ID: {pos.get('pos_ID')}")
```

### Retrieving POS Orders

```python
# Get orders for a specific POS
for pos_config in pos_configs:
    if pos_config.get('pos_type') == 'pos':
        orders = pos_client.get_pos_orders(pos_config, "retail_db")
        
        print(f"\nOrders for POS: {pos_config.get('pos_name')}")
        
        if 'newest' in orders and orders['newest']:
            newest = orders['newest'][0]
            print(f"Latest order: {newest['name']} on {newest['date_order']}")
            
        if 'oldest' in orders and orders['oldest']:
            oldest = orders['oldest'][0]
            print(f"First order: {oldest['name']} on {oldest['date_order']}")
```

## Reporting

### Generating Sales Reports

```python
# Get sales by customer for the last month
from datetime import datetime, timedelta

today = datetime.now()
last_month = today - timedelta(days=30)

# Format dates for Odoo domain
date_from = last_month.strftime('%Y-%m-%d')
date_to = today.strftime('%Y-%m-%d')

# Get sales data
sales_data = client.search_read(
    model='sale.report',
    domain=[
        ('date', '>=', date_from),
        ('date', '<=', date_to),
        ('state', 'in', ['sale', 'done'])
    ],
    fields=['partner_id', 'user_id', 'product_id', 'product_uom_qty', 'price_total'],
    groupby=['partner_id']
)

# Process and display the report
print(f"Sales Report ({date_from} to {date_to}):")
print("-" * 50)
for entry in sales_data:
    partner = entry['partner_id'][1] if isinstance(entry['partner_id'], list) else 'Unknown'
    total = entry['price_total']
    print(f"{partner}: ${total:.2f}")
```

## Batch Processing

### Batch Creation of Records

```python
# Create multiple products at once
product_data = [
    {'name': 'Product A', 'list_price': 10.0, 'default_code': 'A001'},
    {'name': 'Product B', 'list_price': 20.0, 'default_code': 'B002'},
    {'name': 'Product C', 'list_price': 30.0, 'default_code': 'C003'},
    # Add more products as needed
]

# Create products in batch
product_ids = []
for data in product_data:
    product_id = client.create('product.product', data)
    product_ids.append(product_id)

print(f"Created {len(product_ids)} products")
```

### Batch Updates

```python
# Update multiple products at once
update_data = {'categ_id': new_category_id}

success = client.write(
    model='product.product',
    ids=product_ids,
    values=update_data
)

print(f"Batch update successful: {success}")
```

### Creating Multiple Records

```python
# Create multiple products at once
products_to_create = [
    {'name': 'Product A', 'list_price': 10.0, 'default_code': 'PA001'},
    {'name': 'Product B', 'list_price': 20.0, 'default_code': 'PB001'},
    {'name': 'Product C', 'list_price': 30.0, 'default_code': 'PC001'},
]

product_ids = client.create_batch(
    model='product.product',
    values_list=products_to_create
)
print(f"Created {len(product_ids)} products")
```

### Updating Multiple Records

```python
# Update price on multiple products
products_to_update = [
    (product_id1, {'list_price': 15.0}),
    (product_id2, {'list_price': 25.0}),
    (product_id3, {'list_price': 35.0}),
]

for product_id, values in products_to_update:
    client.write(
        model='product.product',
        ids=[product_id],
        values=values
    )
```

## Error Handling

```python
from dgt_rpc import DgtClient, DgtException

client = DgtClient(
    url="https://your-dgtera-instance.com",
    db="your_database",
    api_key="your_api_key"
)

try:
    # Try to create a product with invalid data
    product_id = client.create(
        model='product.product',
        values={
            'name': 'Test Product',
            'list_price': 'not_a_number',  # This should be a float
        }
    )
except DgtException as e:
    print(f"Error creating product: {e}")
    # Handle the error appropriately
```

## Advanced Use Cases

### Custom Model Methods

```python
# Call a custom method on a model
result = client.execute(
    model='sale.order',
    method='action_confirm',
    [order_id]
)

# Call a method with keyword arguments
result = client.execute_kw(
    model='account.move',
    method='action_post',
    args=[[invoice_id]],
    kwargs={'date': '2023-12-31'}
)
```

### Working with Reports

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

These examples demonstrate common usage patterns for the DGT RPC Client. For more specific use cases or advanced functionality, refer to the [API Reference](api_reference.md) and [Advanced Usage](advanced_usage.md) documentation. 