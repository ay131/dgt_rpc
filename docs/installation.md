# Installation Guide

This guide provides detailed instructions for installing the DGT RPC Client library.

## System Requirements

- Python 3.6 or later
- pip (Python package installer)
- Internet connection for downloading packages

## Standard Installation

The simplest way to install the DGT RPC Client is using pip:
```bash
pip install dgt-rpc
```

To install a specific version:

```bash
pip install dgt-rpc==1.0.0
```

## Installation in a Virtual Environment

It's recommended to install the package in a virtual environment to avoid conflicts with other Python packages:

### Using venv (Python 3.6+)

```bash
# Create a virtual environment
python -m venv dgt-env

# Activate the environment
# On Windows:
dgt-env\Scripts\activate
# On macOS/Linux:
source dgt-env/bin/activate

# Install the package
pip install dgt-rpc
```

### Using conda

```bash
# Create a conda environment
conda create -n dgt-env python=3.9

# Activate the environment
conda activate dgt-env

# Install the package
pip install dgt-rpc
```

## Installing from Source

For the latest development version or to contribute to the project:

```bash
# Clone the repository
git clone https://github.com/dgtera/dgt-rpc.git
cd dgt-rpc

# Install in development mode
pip install -e .
```

## Verifying Installation

You can verify that the installation was successful by importing the package in Python:

```python
import dgt_rpc
print(dgt_rpc.__version__)
```

## Dependencies

The DGT RPC Client has the following dependencies, which will be automatically installed:

- requests>=2.25.0
- xmlrpc>=1.0.1
- python-dotenv>=0.15.0

## Troubleshooting

### Common Installation Issues

1. **Permission Errors**: If you encounter permission errors during installation, try:
   ```bash
   pip install --user dgt-rpc
   ```

2. **SSL Certificate Errors**: If you're behind a corporate firewall or proxy:
   ```bash
   pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org dgt-rpc
   ```

3. **Dependency Conflicts**: If you have dependency conflicts, consider using a virtual environment as described above.

### Getting Help

If you encounter any issues during installation:

1. Check the [Troubleshooting](troubleshooting.md) guide
2. Visit our [GitHub Issues](https://github.com/dgtera/dgt-rpc/issues) page
3. Contact [support](support.md)

## Next Steps

After installation, check out the [Getting Started](getting_started.md) guide to begin using the DGT RPC Client.
