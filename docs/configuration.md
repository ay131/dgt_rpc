# Configuration

The DGT RPC Client offers several ways to configure your connection to DgteraERP systems. This document explains all available configuration methods and options.

## Configuration Methods

You can configure the DGT RPC Client in three main ways:

1. Direct initialization
2. Environment variables
3. Configuration files

### 1. Direct Initialization

The most straightforward way to configure the client is by passing parameters directly when creating an instance:

```python
from dgt_rpc import DgtClient

client = DgtClient(
    url="https://your-dgtera-instance.com",
    db="your_database",
    username="your_username",
    password="your_password"
    # OR
    # api_key="your_api_key"
)
```

### 2. Environment Variables

You can set environment variables to configure the client:

```python
import os
from dgt_rpc import DgtClient

os.environ['DGTERA_URL'] = "https://your-dgtera-instance.com"
os.environ['DGTERA_DB'] = "your_database"
os.environ['DGTERA_API_KEY'] = "your_api_key"
# OR
# os.environ['DGTERA_USERNAME'] = "your_username"
# os.environ['DGTERA_PASSWORD'] = "your_password"

# Client will use environment variables if no parameters are provided
client = DgtClient.from_environment()
```

Available environment variables:
- `DGTERA_URL`: The URL of the Dgterainstance
- `DGTERA_DB`: The database name
- `DGTERA_USERNAME`: The username for authentication
- `DGTERA_PASSWORD`: The password for authentication
- `DGTERA_API_KEY`: API key for authentication
- `DGTERA_TIMEOUT`: Connection timeout in seconds
- `DGTERA_MAX_RETRIES`: Maximum number of retry attempts
- `DGTERA_RETRY_DELAY`: Delay between retries in seconds

### 3. Configuration Files

You can create a configuration file to store your connection settings. By default, the client looks for a file at `~/.dgt_rpc.conf`, but you can specify a different path.

Example configuration file:

```ini
[default]
url = https://your-dgtera-instance.com
db = your_database
api_key = your_api_key

[production]
url = https://production.dgtera.com
db = prod_db
username = admin
password = secure_password

[development]
url = https://dev.dgtera.com
db = dev_db
username = developer
password = dev_password
timeout = 60
max_retries = 5
retry_delay = 2
```

Then load the configuration:

```python
from dgt_rpc import DgtClient

# Load the default profile
client = DgtClient.from_config()

# Or specify a profile
prod_client = DgtClient.from_config(profile="production")

# Or specify a different configuration file
dev_client = DgtClient.from_config(
    config_file="/path/to/custom/config.conf",
    profile="development"
)
```

## Configuration Parameters

The following parameters can be configured:

### Connection Parameters

- `url` (str): The URL of the Dgterainstance
- `db` (str): The database name

### Authentication Parameters

- `username` (str): The username for authentication
- `password` (str): The password for authentication
- `api_key` (str): API key for authentication (alternative to username/password)

### Network Parameters

- `timeout` (int): Connection timeout in seconds. Default: 120
- `max_retries` (int): Maximum number of retry attempts for failed requests. Default: 3
- `retry_delay` (int): Delay between retries in seconds. Default: 1

## Configuration Priority

When multiple configuration methods are used, the client follows this priority order:

1. Direct parameters passed to the constructor
2. Parameters passed to `from_environment()` or `from_config()`
3. Environment variables (for `from_environment()`)
4. Configuration file settings (for `from_config()`)
5. Default values

## Multiple Connections

You can create multiple client instances to connect to different Dgterainstances:

```python
# Production instance
prod_client = DgtClient(
    url="https://production.dgtera.com",
    db="prod_db",
    api_key="prod_api_key"
)

# Development instance
dev_client = DgtClient(
    url="https://dev.dgtera.com",
    db="dev_db",
    api_key="dev_api_key"
)

# Use clients as needed
prod_partners = prod_client.search_read('res.partner', limit=5)
dev_partners = dev_client.search_read('res.partner', limit=5)
```

## Secure Configuration

For production environments, consider these security best practices:

1. **Use API Keys**: API keys are generally more secure than username/password authentication
2. **Environment Variables**: Use environment variables instead of hardcoding credentials
3. **Configuration Files**: If using configuration files, ensure they have restricted permissions:
   ```bash
   chmod 600 ~/.dgt_rpc.conf
   ```
4. **Secrets Management**: For production systems, consider using a secrets management solution

## Dynamic Configuration

You can change configuration at runtime:

```python
client = DgtClient(url="https://your-dgtera-instance.com")

# Connect to different databases as needed
client.db = "database1"
client.api_key = "api_key_for_db1"
client.authenticate()

# Do operations on database1
partners_db1 = client.search_read('res.partner', limit=5)

# Switch to another database
client.db = "database2"
client.api_key = "api_key_for_db2"
client.authenticate()

# Do operations on database2
partners_db2 = client.search_read('res.partner', limit=5)
``` 