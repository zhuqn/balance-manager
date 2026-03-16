"""
OpenRouter API provider for balance checking.

OpenRouter provides a REST API for checking API key balance and usage.
Documentation: https://openrouter.ai/docs
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


class OpenRouterProvider(BalanceProvider):
    """
    Provider for OpenRouter AI platform.
    
    OpenRouter API endpoints:
    - GET /api/v1/auth/key - Get API key info including balance
    """
    
    BASE_URL = "https://openrouter.ai/api/v1"
    
    @property
    def platform_name(self) -> str:
        return "openrouter"
    
    def get_balance(self) -> PlatformBalance:
        """
        Fetch balance from OpenRouter API.
        
        Returns:
            PlatformBalance with current balance information.
            
        Raises:
            AuthenticationError: If API key is invalid.
            RateLimitError: If rate limit exceeded.
            ProviderError: For other errors.
        """
        if not self.api_key:
            raise AuthenticationError(
                self.platform_name,
                "API key is required for OpenRouter"
            )
        
        url = f"{self.BASE_URL}/auth/key"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=self.timeout)
            
            if response.status_code == 401:
                raise AuthenticationError(
                    self.platform_name,
                    "Invalid API key"
                )
            elif response.status_code == 429:
                retry_after = int(response.headers.get("Retry-After", 60))
                raise RateLimitError(
                    self.platform_name,
                    "Rate limit exceeded",
                    retry_after
                )
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
        """
        Parse OpenRouter API response.
        
        Response format:
        {
            "data": {
                "limit": "100.00",
                "usage": "25.50",
                ...
            }
        }
        """
        raw_data = data
        balance_data = data.get("data", {})
        
        # OpenRouter returns limit and usage as strings
        limit_str = balance_data.get("limit", "0")
        usage_str = balance_data.get("usage", "0")
        
        # Parse limit (total balance)
        try:
            limit = float(limit_str) if limit_str else 0.0
        except ValueError:
            limit = 0.0
        
        # Parse usage
        try:
            usage = float(usage_str) if usage_str else 0.0
        except ValueError:
            usage = 0.0
        
        # Calculate remaining balance
        remaining = limit - usage
        
        return PlatformBalance(
            platform=self.platform_name,
            account_id=balance_data.get("label", ""),
            balance=remaining,
            currency="USD",
            usage_this_month=usage,
            usage_total=usage,
            last_updated=datetime.now(),
            status=BalanceStatus.ACTIVE,
            raw_data=raw_data,
        )
    
    def get_usage(self, start_date: date, end_date: date) -> UsageReport:
        """
        Get usage report for a date range.
        
        Note: OpenRouter API doesn't provide detailed usage breakdown by date.
        """
        balance = self.get_balance()
        
        return UsageReport(
            platform=self.platform_name,
            start_date=start_date,
            end_date=end_date,
            total_usage=balance.usage_total,
            currency="USD",
        )
