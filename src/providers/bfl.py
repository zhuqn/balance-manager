"""
BFL (Kontext) API provider for balance checking.
"""

import requests
from datetime import datetime, date
from typing import Dict, Any

# Import with fallback for direct module execution
try:
    from .base import BalanceProvider
    from core.models import PlatformBalance, UsageReport, BalanceStatus
    from core.exceptions import AuthenticationError, RateLimitError, ProviderError
except ImportError:
    from ..core.models import PlatformBalance, UsageReport, BalanceStatus
    from ..core.exceptions import AuthenticationError, RateLimitError, ProviderError
    from .base import BalanceProvider


class BFLProvider(BalanceProvider):
    """Provider for BFL (Kontext) platform."""
    
    BASE_URL = "https://api.bfl.ai/v1"
    
    @property
    def platform_name(self) -> str:
        return "bfl"
    
    def get_balance(self) -> PlatformBalance:
        """Fetch balance from BFL API."""
        if not self.api_key:
            raise AuthenticationError(self.platform_name, "API key is required")
        
        url = f"{self.BASE_URL}/balance"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=self.timeout)
            
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
        """Parse BFL API response."""
        balance = 0.0
        currency = "USD"
        
        if "balance" in data:
            balance = float(data.get("balance", 0))
        elif "credits" in data:
            balance = float(data.get("credits", 0))
        elif "data" in data and "balance" in data["data"]:
            balance = float(data["data"]["balance"])
        
        currency = data.get("currency", "USD")
        
        return PlatformBalance(
            platform=self.platform_name,
            balance=balance,
            currency=currency,
            last_updated=datetime.now(),
            status=BalanceStatus.ACTIVE,
            raw_data=data,
        )
    
    def get_usage(self, start_date: date, end_date: date) -> UsageReport:
        """Get usage report."""
        return UsageReport(
            platform=self.platform_name,
            start_date=start_date,
            end_date=end_date,
            total_usage=0.0,
            currency="USD",
        )
