"""
Volcengine (火山方舟) API provider for balance checking.
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


class VolcengineProvider(BalanceProvider):
    """Provider for Volcengine (火山方舟) platform."""
    
    BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"
    
    @property
    def platform_name(self) -> str:
        return "volcengine"
    
    def get_balance(self) -> PlatformBalance:
        """Fetch balance from Volcengine API."""
        if not self.api_key:
            raise AuthenticationError(self.platform_name, "API key is required")
        
        url = f"{self.BASE_URL}/balance"
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
        """Parse Volcengine API response."""
        try:
            available = float(data.get("available_balance", 0) or 0)
        except (ValueError, TypeError):
            available = 0.0
        
        try:
            total = float(data.get("total_balance", 0) or 0)
        except (ValueError, TypeError):
            total = 0.0
        
        currency = data.get("currency", "CNY")
        
        return PlatformBalance(
            platform=self.platform_name,
            balance=available,
            currency=currency,
            usage_total=total - available if total > available else 0.0,
            last_updated=datetime.now(),
            status=BalanceStatus.ACTIVE,
            raw_data=data,
        )
    
    def get_usage(self, start_date: date, end_date: date) -> UsageReport:
        """Get usage report - not available in public API."""
        return UsageReport(
            platform=self.platform_name,
            start_date=start_date,
            end_date=end_date,
            total_usage=0.0,
            currency="CNY",
        )
