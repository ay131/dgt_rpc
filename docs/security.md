# Security

This document outlines security considerations and best practices when using the DGT RPC Client.

## Authentication Security

### API Keys vs. Username/Password

The DGT RPC Client supports two authentication methods:

1. **API Key Authentication** (Recommended)
   - More secure as it doesn't expose the user's password
   - Can be revoked without changing the user's password
   - Can have limited permissions compared to the user's full access

2. **Username/Password Authentication**
   - Simpler to implement
   - Requires storing the user's actual password
   - If compromised, requires changing the user's password

We strongly recommend using API key authentication for production environments.

### Storing Credentials Securely

Never hardcode credentials in your source code. Instead:

- Use environment variables
- Use a secure configuration file with restricted permissions
- Use a secrets management system

Example using environment variables:

```python
import os
from dgt_rpc import DgtClient

client = DgtClient(
    url=os.environ.get('DGTERA_URL'),
    db=os.environ.get('DGTERA_DB'),
    api_key=os.environ.get('DGTERA_API_KEY')
)
```

## Network Security

### HTTPS

Always use HTTPS URLs when connecting to your DgteraERP instance. Using HTTP exposes your authentication credentials and data to potential interception.

### Firewalls and IP Restrictions

Consider restricting XML-RPC access to your DgteraERP instance by IP address if possible. This can be done at the network level or using web server configuration.

## Access Control

### Principle of Least Privilege

Create dedicated API users with only the permissions they need:

1. Create a specific user for API access
2. Assign only the necessary groups and permissions
3. Use record rules to restrict access to sensitive data

### Regular Credential Rotation

Regularly rotate API keys and passwords to limit the impact of potential credential leaks.

## Data Security

### Sensitive Data Handling

Be cautious when handling sensitive data:

- Only request the fields you need
- Don't log sensitive information
- Clear sensitive data from memory when no longer needed

### Input Validation

Always validate input data before sending it to the server:

```python
def create_partner(client, name, email):
    # Validate input
    if not name or len(name) > 100:
        raise ValueError("Invalid name")
    
    if email and '@' not in email:
        raise ValueError("Invalid email format")
    
    # Proceed with creation
    return client.create('res.partner', {
        'name': name,
        'email': email
    })
```

## Reporting Security Issues

If you discover a security vulnerability in the DGT RPC Client, please send an email to security@dgtera.com. Do not disclose security vulnerabilities publicly until they have been handled by the maintainers.

## Security Checklist

- [ ] Use HTTPS for all connections
- [ ] Use API keys instead of username/password where possible
- [ ] Store credentials securely (not in code)
- [ ] Create dedicated API users with minimal permissions
- [ ] Implement proper error handling to avoid information leakage
- [ ] Validate all input data
- [ ] Keep the library updated to the latest version
- [ ] Regularly rotate credentials
- [ ] Implement proper logging (without sensitive data)
- [ ] Consider implementing request rate limiting

By following these security best practices, you can minimize the risk when using the DGT RPC Client to interact with your DgteraERP systems. 