# Getting Started with DGT RPC Client

This guide will help you get up and running with the DGT RPC Client quickly.

## Basic Setup

After [installing](installation.md) the DGT RPC Client, you can create your first connection:

```python
from dgt_rpc import DgtClient

# Create a client
client = DgtClient(
    url="https://your-dgtera-instance.com",
    db="your_database",
    api_key="your_api_key"
)

# Authenticate
uid = client.authenticate()
if uid:
    print(f"Successfully authenticated with UID: {uid}")
```

## First Operations

### Reading Records

```python
# Search for partners
partners = client.search_read(
    model='res.partner',
    domain=[('customer_rank', '>', 0)],
    fields=['name', 'email', 'phone'],
    limit=5
)

# Display results
for partner in partners:
    print(f"Partner: {partner['name']}, Email: {partner.get('email', 'N/A')}")
```

### Creating Records

```python
# Create a new product
product_id = client.create(
    model='product.product',
    values={
        'name': 'New Product',
        'list_price': 99.99,
        'default_code': 'NP001',
    }
)
print(f"Created product with ID: {product_id}")
```

### Updating Records

```python
# Update a product
success = client.write(
    model='product.product',
    ids=[product_id],
    values={'list_price': 89.99}
)
if success:
    print("Product updated successfully")
```

## Next Steps

- Check out the [Usage Examples](usage_examples.md) for more complex scenarios
- Learn about [Configuration](configuration.md) options
- Explore the [API Reference](api_reference.md) for detailed information

## Common Issues

If you encounter authentication problems, ensure:
1. Your URL is correct and includes the protocol (https://)
2. Your database name is spelled correctly
3. Your API key or username/password credentials are valid

For more troubleshooting help, see the [Troubleshooting](troubleshooting.md) guide. 