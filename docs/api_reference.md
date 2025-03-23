# API Reference

This document provides detailed information about the classes, methods, and parameters available in the DGT RPC Client.

## Table of Contents

- [DgtClient](#dgtclient)
  - [Constructor](#constructor)
  - [Authentication Methods](#authentication-methods)
  - [Core Methods](#core-methods)
  - [Convenience Methods](#convenience-methods)
- [DgtPOSClient](#dgtposclient)
  - [Constructor](#posclient-constructor)
  - [POS Methods](#pos-methods)
- [Exceptions](#exceptions)

## DgtClient

The main client class for interacting with DgteraERP systems.

### Constructor

```python
DgtClient(
    url=None,
    db=None,
    username=None,
    password=None,
    api_key=None,
    timeout=120,
    max_retries=3,
    retry_delay=1
)
```

#### Parameters:

- `url` (str, optional): The URL of the Dgterainstance
- `db` (str, optional): The database name
- `username` (str, optional): The username for authentication
- `password` (str, optional): The password for authentication
- `api_key` (str, optional): API key for authentication (alternative to username/password)
- `timeout` (int, optional): Connection timeout in seconds. Default: 120
- `max_retries` (int, optional): Maximum number of retry attempts for failed requests. Default: 3
- `retry_delay` (int, optional): Delay between retries in seconds. Default: 1

### Class Methods

#### from_environment

```python
@classmethod
def from_environment(cls, **kwargs)
```

Creates a client instance using environment variables.

Environment variables used:
- `DGTERA_URL`: The URL of the Dgterainstance
- `DGTERA_DB`: The database name
- `DGTERA_USERNAME`: The username for authentication
- `DGTERA_PASSWORD`: The password for authentication
- `DGTERA_API_KEY`: API key for authentication

#### from_config

```python
@classmethod
def from_config(cls, config_file=None, profile="default", **kwargs)
```

Creates a client instance using a configuration file.

Parameters:
- `config_file` (str, optional): Path to the configuration file. Default: ~/.dgt_rpc.conf
- `profile` (str, optional): Configuration profile to use. Default: "default"

### Instance Methods

#### authenticate

```python
def authenticate(self, db=None, username=None, password=None, api_key=None)
```

Authenticates with the Dgteraserver.

Parameters:
- `db` (str, optional): Database name (overrides instance attribute)
- `username` (str, optional): Username (overrides instance attribute)
- `password` (str, optional): Password (overrides instance attribute)
- `api_key` (str, optional): API key (overrides instance attribute)

Returns:
- `int`: User ID if authentication is successful

#### search

```python
def search(self, model, domain=None, offset=0, limit=None, order=None)
```

Searches for records of the specified model.

Parameters:
- `model` (str): The model name
- `domain` (list, optional): Search domain. Default: []
- `offset` (int, optional): Number of records to skip. Default: 0
- `limit` (int, optional): Maximum number of records to return. Default: None
- `order` (str, optional): Sort order. Default: None

Returns:
- `list`: List of record IDs

#### read

```python
def read(self, model, ids, fields=None)
```

Reads record data.

Parameters:
- `model` (str): The model name
- `ids` (list): List of record IDs to read
- `fields` (list, optional): List of fields to read. Default: None (all fields)

Returns:
- `list`: List of dictionaries containing the record data

#### search_read

```python
def search_read(self, model, domain=None, fields=None, offset=0, limit=None, order=None)
```

Combines search and read operations.

Parameters:
- `model` (str): The model name
- `domain` (list, optional): Search domain. Default: []
- `fields` (list, optional): List of fields to read. Default: None (all fields)
- `offset` (int, optional): Number of records to skip. Default: 0
- `limit` (int, optional): Maximum number of records to return. Default: None
- `order` (str, optional): Sort order. Default: None

Returns:
- `list`: List of dictionaries containing the record data

#### create

```python
def create(self, model, values)
```

Creates a new record.

Parameters:
- `model` (str): The model name
- `values` (dict): Field values for the new record

Returns:
- `int`: ID of the created record

#### write

```python
def write(self, model, ids, values)
```

Updates existing records.

Parameters:
- `model` (str): The model name
- `ids` (list): List of record IDs to update
- `values` (dict): Field values to update

Returns:
- `bool`: True if successful

#### unlink

```python
def unlink(self, model, ids)
```

Deletes records.

Parameters:
- `model` (str): The model name
- `ids` (list): List of record IDs to delete

Returns:
- `bool`: True if successful

#### create_batch

```python
def create_batch(self, model, values_list, batch_size=100)
```

Creates multiple records efficiently.

Parameters:
- `model` (str): The model name
- `values_list` (list): List of dictionaries containing field values
- `batch_size` (int, optional): Number of records to create in each batch. Default: 100

Returns:
- `list`: List of created record IDs

#### execute

```python
def execute(self, model, method, *args)
```

Executes a method on a model.

Parameters:
- `model` (str): The model name
- `method` (str): The method name
- `*args`: Arguments to pass to the method

Returns:
- Result of the method call

#### execute_kw

```python
def execute_kw(self, model, method, args=None, kwargs=None)
```

Executes a method on a model with keyword arguments.

Parameters:
- `model` (str): The model name
- `method` (str): The method name
- `args` (list, optional): Positional arguments. Default: None
- `kwargs` (dict, optional): Keyword arguments. Default: None

Returns:
- Result of the method call

#### ref

```python
def ref(self, xml_id)
```

Gets the database ID from an XML ID.

Parameters:
- `xml_id` (str): The XML ID

Returns:
- `int`: The database ID

## DgtPOSClient

A specialized client for working with Point of Sale systems.

### Constructor

```python
DgtPOSClient(
    url=None,
    db=None,
    username=None,
    password=None,
    api_key=None,
    timeout=120,
    max_retries=3,
    retry_delay=1
)
```

Inherits all parameters from DgtClient.

### Instance Methods

#### get_pos_data

```python
def get_pos_data(self, target_db, active_only=True)
```

Gets POS configuration data.

Parameters:
- `target_db` (str): Target database name
- `active_only` (bool, optional): Whether to return only active POS configurations. Default: True

Returns:
- `list`: List of POS configuration dictionaries

#### get_pos_orders

```python
def get_pos_orders(self, pos_config, target_db, limit=10, include_lines=True)
```

Gets orders for a specific POS configuration.

Parameters:
- `pos_config` (dict or int): POS configuration dictionary or ID
- `target_db` (str): Target database name
- `limit` (int, optional): Maximum number of orders to return. Default: 10
- `include_lines` (bool, optional): Whether to include order lines. Default: True

Returns:
- `dict`: Dictionary containing order data categorized as 'newest', 'oldest', and 'all'

## DgtException

Exception class for DGT RPC Client errors.

### Constructor

```python
DgtException(message, code=None, data=None)
```

Parameters:
- `message` (str): Error message
- `code` (int, optional): Error code. Default: None
- `data` (dict, optional): Additional error data. Default: None

For more detailed information about the implementation of these classes and methods, refer to the source code documentation. 