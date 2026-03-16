"""
Base provider interface for all balance providers.

All platform-specific providers must inherit from this abstract base class.

Note: Using synchronous requests library for Python 3.6 compatibility.
"""

from abc import ABC, abstractmethod
from datetime import datetime, date
from typing import Optional, Dict, Any

# Import with fallback for direct module execution
try:
    from core.models import PlatformBalance, UsageReport, BalanceStatus
except ImportError:
    from ..core.models import PlatformBalance, UsageReport, BalanceStatus


class BalanceProvider(ABC):
    """
    Abstract base class for all balance providers.
    
    Subclasses must implement:
    - get_balance(): Fetch current balance
    - get_usage(): Fetch usage report for a date range
    - platform_name: Property returning platform identifier
    
    Attributes:
        api_key: API key for authentication.
        base_url: Base URL for API requests.
        timeout: Request timeout in seconds.
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: int = 30,
    ):
        """
        Initialize the provider.
        
        Args:
            api_key: API key for authentication.
            base_url: Optional override for base API URL.
            timeout: Request timeout in seconds.
        """
        self.api_key = api_key
        self.base_url = base_url
        self.timeout = timeout
    
    @property
    @abstractmethod
    def platform_name(self) -> str:
        """
        Return the platform identifier.
        
        Returns:
            Unique platform name (e.g., 'openrouter', 'minimax').
        """
        pass
    
    @abstractmethod
    def get_balance(self) -> PlatformBalance:
        """
        Fetch the current balance for this platform.
        
        Returns:
            PlatformBalance object with current balance information.
            
        Raises:
            AuthenticationError: If API key is invalid.
            RateLimitError: If rate limit is exceeded.
            ProviderError: For other API errors.
        """
        pass
    
    @abstractmethod
    def get_usage(
        self,
        start_date: date,
        end_date: date,
    ) -> UsageReport:
        """
        Fetch usage report for a date range.
        
        Args:
            start_date: Start of the reporting period.
            end_date: End of the reporting period.
            
        Returns:
            UsageReport with usage statistics.
        """
        pass
    
    def _get_default_headers(self) -> Dict[str, str]:
        """
        Get default headers for API requests.
        
        Returns:
            Dictionary of default headers.
        """
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "BalanceManager/1.0",
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers
    
    def _parse_balance_response(self, data: Dict[str, Any]) -> PlatformBalance:
        """
        Parse API response into PlatformBalance.
        
        Subclasses should override this to handle their specific response format.
        
        Args:
            data: Raw API response data.
            
        Returns:
            PlatformBalance object.
        """
        return PlatformBalance(
            platform=self.platform_name,
            balance=float(data.get("balance", 0.0)),
            currency=data.get("currency", "USD"),
            raw_data=data,
            status=BalanceStatus.ACTIVE,
            last_updated=datetime.now(),
        )
