"""
Balance Manager - Core coordinator for all balance providers.

Synchronous version for Python 3.6 compatibility.
"""

from datetime import datetime
from typing import Dict, List, Optional, Type
from pathlib import Path

from .models import PlatformBalance, BalanceStatus, SystemSummary, PlatformConfig
from .exceptions import ProviderError, ConfigurationError, ManualEntryRequired

# Import BalanceProvider with fallback for direct module execution
try:
    from providers.base import BalanceProvider
except ImportError:
    from ..providers.base import BalanceProvider


class BalanceManager:
    """
    Central coordinator for managing balances across multiple platforms.
    """
    
    def __init__(
        self,
        warning_threshold: float = 100.0,
        critical_threshold: float = 50.0,
    ):
        """
        Initialize the BalanceManager.
        
        Args:
            warning_threshold: Balance below this triggers WARNING status.
            critical_threshold: Balance below this triggers CRITICAL status.
        """
        self.providers: Dict[str, BalanceProvider] = {}
        self.configs: Dict[str, PlatformConfig] = {}
        self.warning_threshold = warning_threshold
        self.critical_threshold = critical_threshold
        self._last_check: Optional[datetime] = None
    
    def register_provider(self, provider: BalanceProvider, config: PlatformConfig) -> None:
        """Register a provider for a platform."""
        if not config.enabled:
            return
        
        self.providers[config.name] = provider
        self.configs[config.name] = config
    
    def check_balance(self, platform: str) -> PlatformBalance:
        """
        Check balance for a single platform.
        
        Args:
            platform: Platform identifier.
            
        Returns:
            PlatformBalance object with current balance information.
        """
        if platform not in self.providers:
            raise ConfigurationError(platform, f"Provider not registered for '{platform}'")
        
        provider = self.providers[platform]
        
        try:
            balance = provider.get_balance()
            balance.update_status(self.warning_threshold, self.critical_threshold)
            return balance
        except ManualEntryRequired:
            raise
        except Exception as e:
            raise ProviderError(platform, f"Failed to check balance: {str(e)}", e)
    
    def check_all_balances(self) -> List[PlatformBalance]:
        """
        Check balances for all registered platforms.
        
        Returns:
            List of PlatformBalance objects for all platforms.
        """
        if not self.providers:
            return []
        
        balances = []
        for platform in self.providers:
            try:
                balance = self.check_balance(platform)
                balances.append(balance)
            except ManualEntryRequired:
                balances.append(PlatformBalance(
                    platform=platform,
                    status=BalanceStatus.UNKNOWN,
                    last_updated=datetime.now(),
                ))
            except ProviderError:
                balances.append(PlatformBalance(
                    platform=platform,
                    status=BalanceStatus.ERROR,
                    last_updated=datetime.now(),
                ))
        
        self._last_check = datetime.now()
        return balances
    
    def get_summary(self, balances: List[PlatformBalance]) -> SystemSummary:
        """
        Generate a system summary from balance data.
        
        Args:
            balances: List of PlatformBalance objects.
            
        Returns:
            SystemSummary with aggregated statistics.
        """
        summary = SystemSummary()
        summary.update_from_balances(balances)
        summary.generated_at = datetime.now()
        return summary
    
    def check_and_summarize(self) -> SystemSummary:
        """
        Check all balances and generate a summary.
        
        Returns:
            SystemSummary with current state of all platforms.
        """
        balances = self.check_all_balances()
        return self.get_summary(balances)
    
    @property
    def last_check(self) -> Optional[datetime]:
        """Get the timestamp of the last balance check."""
        return self._last_check
    
    def get_platform_names(self) -> List[str]:
        """Get list of all registered platform names."""
        return list(self.providers.keys())
    
    def get_enabled_platforms(self) -> List[str]:
        """Get list of enabled platform names."""
        return [name for name, config in self.configs.items() if config.enabled]
    
    def get_manual_entry_platforms(self) -> List[str]:
        """Get list of platforms that require manual entry."""
        return [name for name, config in self.configs.items() if config.method == "manual"]
    
    def get_api_platforms(self) -> List[str]:
        """Get list of platforms with API support."""
        return [name for name, config in self.configs.items() if config.method == "api"]
