# Frequently Asked Questions

This document addresses common questions and issues that users might encounter when working with the DGT RPC Client.

## General Questions

### What is DGT RPC Client?
DGT RPC Client is a Python library that provides a convenient interface for interacting with DgteraERP systems via XML-RPC protocol. It's specifically designed for DGTera environments and includes specialized functionality for POS management.

### What Python versions are supported?
DGT RPC Client supports Python 3.6 and later versions.

### Is this library official?
Yes, this is the official DGT RPC Client library maintained by DGTera.

## Authentication

### What authentication methods are supported?
The library supports two authentication methods:
1. Username and password authentication
2. API key authentication

### Which authentication method should I use?
API key authentication is recommended for production environments as it's more secure and doesn't require storing a user's password in your code or configuration files.

### My authentication is failing, what should I check?
- Verify that the URL, database name, and credentials are correct
- Ensure the user has the necessary access rights in the DgteraERP system
- Check if the API key is valid and not expired
- Verify network connectivity to the DgteraERP server

## Usage

### How do I handle connection timeouts?
You can implement retry logic around the client methods:

```python
import time
from dgt_rpc import DgtClient, DgtException

client = DgtClient(url="https://your-instance.com", db="your_db", api_key="your_key")

max_retries = 3
retry_delay = 2  # seconds

for attempt in range(max_retries):
    try:
        result = client.search_read(...)
        break  # Success, exit the retry loop
    except DgtException as e:
        if attempt < max_retries - 1:  # Don't sleep on the last attempt
            print(f"Attempt {attempt+1} failed: {e}. Retrying in {retry_delay} seconds...")
            time.sleep(retry_delay)
        else:
            print(f"All {max_retries} attempts failed.")
            raise
```

### How can I optimize performance for multiple operations?
- Reuse the same client instance for multiple operations
- Use `search_read` instead of separate `search` and `read` calls
- Specify only the fields you need when reading records
- Use appropriate limits and pagination for large datasets

### Can I use this library with standard Odoo instances?
While this library is optimized for DgteraERP systems, it should work with standard Odoo instances as well, as they use the same XML-RPC protocol. However, some specialized methods like those in the `DgtPOSClient` class may not be applicable.

## Troubleshooting

### I'm getting SSL certificate errors
If you're encountering SSL certificate validation errors, you might be behind a corporate firewall or using a self-signed certificate. You can modify your code to handle this:

```python
import ssl
import xmlrpc.client

# Create a context that doesn't verify SSL certificates (use with caution)
context = ssl._create_unverified_context()

# Modify the client's ServerProxy instances
client.common = xmlrpc.client.ServerProxy(f'{client.url}/xmlrpc/2/common', context=context)
client.models = xmlrpc.client.ServerProxy(f'{client.url}/xmlrpc/2/object', context=context)
```

Note: Disabling SSL verification reduces security. Use this approach only in controlled environments.

### How do I debug XML-RPC calls?
You can enable logging to see the details of XML-RPC calls:

```python
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('xmlrpc.client')
logger.setLevel(logging.DEBUG)
```

## Support and Contributions

### How do I report a bug?
Please report bugs by opening an issue on our [GitHub repository](https://github.com/dgtera/dgt-rpc/issues).

### Can I contribute to this project?
Yes! Contributions are welcome. Please see our [Contributing Guide](contributing.md) for details on how to contribute.

### Where can I get additional help?
If your question isn't answered here, please check the [documentation](README.md) or contact [support](support.md). 