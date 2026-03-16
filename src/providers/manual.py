"""
Manual entry provider for platforms without API support.

This provider allows users to manually enter balance information
for platforms that don't provide API access.
"""

from datetime import datetime, date
from typing import Dict, Any, Optional

# Import with fallback for direct module execution
try:
    from .base import BalanceProvider
    from core.models import PlatformBalance, UsageReport, BalanceStatus
    from core.exceptions import ManualEntryRequired
except ImportError:
    from ..core.models import PlatformBalance, UsageReport, BalanceStatus
    from ..core.exceptions import ManualEntryRequired
    from .base import BalanceProvider


class ManualProvider(BalanceProvider):
    """
    Provider for manual balance entry.
    
    This provider raises ManualEntryRequired to signal that
    the user needs to input balance data manually.
    """
    
    @property
    def platform_name(self) -> str:
        return "manual"
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: int = 30,
        platform_name: str = "unknown",
        stored_balance: Optional[float] = None,
        currency: str = "USD",
    ):
        """
        Initialize manual provider.
        
        Args:
            platform_name: Name of the platform this represents.
            stored_balance: Previously stored balance value.
            currency: Currency for the balance.
        """
        super().__init__(api_key, base_url, timeout)
        self._platform_name = platform_name
        self._stored_balance = stored_balance
        self._currency = currency
    
    @property
    def platform_name(self) -> str:
        return self._platform_name
    
    def get_balance(self) -> PlatformBalance:
        """
        Attempt to get balance.
        
        Raises:
            ManualEntryRequired: Always raised to signal manual entry needed.
        """
        if self._stored_balance is not None:
            # Return stored balance if available
            return PlatformBalance(
                platform=self.platform_name,
                balance=self._stored_balance,
                currency=self._currency,
                status=BalanceStatus.UNKNOWN,  # Unknown because not verified
                last_updated=datetime.now(),
            )
        
        # No stored balance - require manual entry
        raise ManualEntryRequired(
            self.platform_name,
            f"Please enter balance for {self.platform_name} manually"
        )
    
    def set_balance(self, balance: float, currency: str = "USD") -> PlatformBalance:
        """
        Set balance manually.
        
        Args:
            balance: Balance amount to set.
            currency: Currency code.
            
        Returns:
            PlatformBalance with the entered value.
        """
        self._stored_balance = balance
        self._currency = currency
        
        return PlatformBalance(
            platform=self.platform_name,
            balance=balance,
            currency=currency,
            status=BalanceStatus.UNKNOWN,
            last_updated=datetime.now(),
        )
    
    def get_usage(self, start_date: date, end_date: date) -> UsageReport:
        """
        Manual providers cannot fetch usage automatically.
        
        Returns:
            Empty UsageReport.
        """
        return UsageReport(
            platform=self.platform_name,
            start_date=start_date,
            end_date=end_date,
            total_usage=0.0,
            currency=self._currency,
        )
    
    def get_last_balance(self) -> Optional[PlatformBalance]:
        """
        Get the last manually entered balance.
        
        Returns:
            PlatformBalance if set, None otherwise.
        """
        if self._stored_balance is None:
            return None
        
        return PlatformBalance(
            platform=self.platform_name,
            balance=self._stored_balance,
            currency=self._currency,
            status=BalanceStatus.UNKNOWN,
            last_updated=datetime.now(),
        )
