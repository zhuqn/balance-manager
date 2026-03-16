"""
Custom exceptions for the balance management system.

All exceptions use English naming and documentation.
"""


class BalanceError(Exception):
    """Base exception for all balance-related errors."""
    pass


class ProviderError(BalanceError):
    """
    Exception raised when a provider encounters an error.
    
    Attributes:
        platform: The platform that caused the error.
        message: Error description.
        original_error: The original exception if any.
    """
    def __init__(self, platform: str, message: str, original_error: Exception = None):
        self.platform = platform
        self.message = message
        self.original_error = original_error
        super().__init__(f"[{platform}] {message}")


class ConfigurationError(BalanceError):
    """
    Exception raised when configuration is invalid or missing.
    
    Attributes:
        key: The configuration key that caused the error.
        message: Error description.
    """
    def __init__(self, key: str, message: str):
        self.key = key
        self.message = message
        super().__init__(f"Configuration error for '{key}': {message}")


class StorageError(BalanceError):
    """
    Exception raised when storage operations fail.
    
    Attributes:
        operation: The operation that failed (read/write/delete).
        path: The file path involved.
        message: Error description.
    """
    def __init__(self, operation: str, path: str, message: str):
        self.operation = operation
        self.path = path
        self.message = message
        super().__init__(f"Storage {operation} failed for '{path}': {message}")


class AuthenticationError(ProviderError):
    """
    Exception raised when authentication fails.
    
    This typically means the API key is invalid or expired.
    """
    def __init__(self, platform: str, message: str = "Authentication failed"):
        super().__init__(platform, message)


class RateLimitError(ProviderError):
    """
    Exception raised when API rate limit is exceeded.
    
    Attributes:
        platform: The platform that rate limited.
        message: Error description.
        retry_after: Seconds to wait before retrying (if provided).
    """
    def __init__(self, platform: str, message: str = "Rate limit exceeded", retry_after: int = None):
        super().__init__(platform, message)
        self.retry_after = retry_after


class ManualEntryRequired(BalanceError):
    """
    Exception raised when a platform requires manual entry.
    
    This is not an error but a signal that the user needs to input data.
    """
    def __init__(self, platform: str, message: str = "Manual entry required for this platform"):
        super().__init__(f"[{platform}] {message}")
