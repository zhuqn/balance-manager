"""
MiniMax (海螺 AI) API provider for balance checking.

MiniMax provides a REST API for checking account balance.
"""

import requests
from datetime import datetime, date
from typing import Dict, Any, Optional

# Import with fallback for direct module execution
try:
    from .base import BalanceProvider
    from core.models import PlatformBalance, UsageReport, BalanceStatus
    from core.exceptions import AuthenticationError, RateLimitError, ProviderError
except ImportError:
    from ..core.models import PlatformBalance, UsageReport, BalanceStatus
    from ..core.exceptions import AuthenticationError, RateLimitError, ProviderError
    from .base import BalanceProvider


class MiniMaxProvider(BalanceProvider):
    """
    Provider for MiniMax (海螺 AI) platform.
    """
    
    BASE_URL = "https://api.minimaxi.com/v1"
    
    @property
    def platform_name(self) -> str:
        return "minimax"
    
    def get_balance(self) -> PlatformBalance:
        """Fetch balance from MiniMax API."""
        if not self.api_key:
            raise AuthenticationError(
                self.platform_name,
                "API key is required for MiniMax"
            )
        
        url = f"{self.BASE_URL}/balance/query"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        
        try:
            response = requests.post(url, headers=headers, json={}, timeout=self.timeout)
            
            if response.status_code == 401:
                raise AuthenticationError(self.platform_name, "Invalid API key")
            elif response.status_code == 429:
                raise RateLimitError(self.platform_name, "Rate limit exceeded")
            elif response.status_code != 200:
                raise ProviderError(
                    self.platform_name,
                    f"API returned status {response.status_code}"
                )
            
            data = response.json()
            return self._parse_balance(data)
            
        except requests.RequestException as e:
            raise ProviderError(self.platform_name, f"Network error: {str(e)}", e)
    
    def _parse_balance(self, data: Dict[str, Any]) -> PlatformBalance:
        """Parse MiniMax API response."""
        raw_data = data
        balance_data = data.get("data", {})
        
        balance = float(balance_data.get("balance", 0.0))
        currency = balance_data.get("currency", "CNY")
        
        return PlatformBalance(
            platform=self.platform_name,
            balance=balance,
            currency=currency,
            last_updated=datetime.now(),
            status=BalanceStatus.ACTIVE,
            raw_data=raw_data,
        )
    
    def get_usage(self, start_date: date, end_date: date) -> UsageReport:
        """Get usage report - not available in MiniMax API."""
        return UsageReport(
            platform=self.platform_name,
            start_date=start_date,
            end_date=end_date,
            total_usage=0.0,
            currency="CNY",
        )
