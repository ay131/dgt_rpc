"""
Exceptions for the DGT RPC client.
"""

import xmlrpc.client

class DgtException(Exception):
    """Base exception for all DGT RPC errors."""
    
    def __init__(self, message, original_exception=None):
        """
        Initialize a new DgtException.
        
        Args:
            message (str): The error message
            original_exception (Exception, optional): The original exception that caused this error
        """
        self.original_exception = original_exception
        
        if original_exception and hasattr(original_exception, '__str__'):
            message = f"{message}: {str(original_exception)}"
            
        super().__init__(message)
    
    @classmethod
    def from_xmlrpc_exception(cls, exception):
        """
        Create a DgtException from an XML-RPC exception.
        
        Args:
            exception: The XML-RPC exception
            
        Returns:
            DgtException: A new exception wrapping the XML-RPC exception
        """
        if isinstance(exception, xmlrpc.client.Fault):
            # Extract the fault message
            fault_msg = exception.faultString if hasattr(exception, 'faultString') else str(exception)
            return cls(f"Odoo Server Error", fault_msg)
        elif isinstance(exception, xmlrpc.client.ProtocolError):
            # Format the protocol error message
            url = exception.url
            code = exception.errcode
            message = exception.errmsg
            return cls(f"Protocol error", f"{code} {message} for {url}")
        else:
            return cls(f"XML-RPC Error", exception) 