import unittest
from unittest.mock import patch, MagicMock
import xmlrpc.client

from dgt_rpc import DgtException

class TestDgtException(unittest.TestCase):
    """Test cases for the DgtException class."""

    def test_basic_exception(self):
        """Test creating a basic DgtException."""
        # Create a simple exception
        exception = DgtException("Test error message")
        
        # Check the message
        self.assertEqual(str(exception), "Test error message")
        
        # Check that it's a proper exception
        with self.assertRaises(DgtException) as context:
            raise DgtException("Test error message")
        
        self.assertEqual(str(context.exception), "Test error message")

    def test_exception_with_original(self):
        """Test creating a DgtException with an original exception."""
        # Create an original exception
        original = ValueError("Original error")
        
        # Create a DgtException wrapping the original
        exception = DgtException("Wrapped error", original_exception=original)
        
        # Check the message
        self.assertEqual(str(exception), "Wrapped error: Original error")
        
        # Check that the original exception is stored
        self.assertEqual(exception.original_exception, original)

    def test_from_xmlrpc_fault(self):
        """Test creating a DgtException from an XML-RPC Fault."""
        # Create an XML-RPC Fault
        fault = xmlrpc.client.Fault(1, "XML-RPC Fault message")
        
        # Create a DgtException from the fault
        exception = DgtException.from_xmlrpc_exception(fault)
        
        # Check the message
        self.assertEqual(str(exception), "Odoo Server Error: XML-RPC Fault message")
        
        # Check that the original exception is stored
        self.assertEqual(exception.original_exception, fault)

    def test_from_protocol_error(self):
        """Test creating a DgtException from a Protocol Error."""
        # Create a Protocol Error
        error = xmlrpc.client.ProtocolError(
            'https://test.dgtera.com', 
            500, 
            'Internal Server Error', 
            {'Content-Type': 'text/html'}
        )
        
        # Create a DgtException from the error
        exception = DgtException.from_xmlrpc_exception(error)
        
        # Check the message
        self.assertEqual(
            str(exception), 
            "Protocol error: 500 Internal Server Error for https://test.dgtera.com"
        )
        
        # Check that the original exception is stored
        self.assertEqual(exception.original_exception, error)

    def test_from_general_exception(self):
        """Test creating a DgtException from a general exception."""
        # Create a general exception
        error = ConnectionError("Failed to connect")
        
        # Create a DgtException from the error
        exception = DgtException.from_xmlrpc_exception(error)
        
        # Check the message
        self.assertEqual(str(exception), "XML-RPC Error: Failed to connect")
        
        # Check that the original exception is stored
        self.assertEqual(exception.original_exception, error)


if __name__ == '__main__':
    unittest.main() 