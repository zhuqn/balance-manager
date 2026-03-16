"""
Data models for the balance management system.

All models use English naming and documentation as per project requirements.
"""

from dataclasses import dataclass, field
from datetime import datetime, date
from enum import Enum
from typing import Optional, Dict, Any, List
import json


class BalanceStatus(Enum):
    """
    Enumeration of possible balance status values.
    
    Members:
        ACTIVE: Balance is healthy, above all thresholds.
        WARNING: Balance is below warning threshold.
        CRITICAL: Balance is critically low, below critical threshold.
        UNKNOWN: Unable to fetch balance information.
        ERROR: Error occurred while fetching balance.
    """
    ACTIVE = "active"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"
    ERROR = "error"


@dataclass
class PlatformBalance:
    """
    Represents the balance information for a single platform.
    
    Attributes:
        platform: Unique platform identifier (e.g., 'openrouter', 'minimax').
        account_id: Account identifier on the platform.
        balance: Current available balance.
        currency: Currency code (USD, CNY, etc.).
        usage_this_month: Usage amount for the current month.
        usage_total: Total lifetime usage.
        last_updated: Timestamp of the last balance update.
        status: Current balance status based on thresholds.
        raw_data: Optional raw response data from the API.
    """
    platform: str
    account_id: str = ""
    balance: float = 0.0
    currency: str = "USD"
    usage_this_month: float = 0.0
    usage_total: float = 0.0
    last_updated: datetime = field(default_factory=datetime.now)
    status: BalanceStatus = BalanceStatus.UNKNOWN
    raw_data: Optional[Dict[str, Any]] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "platform": self.platform,
            "account_id": self.account_id,
            "balance": self.balance,
            "currency": self.currency,
            "usage_this_month": self.usage_this_month,
            "usage_total": self.usage_total,
            "last_updated": self.last_updated.isoformat(),
            "status": self.status.value,
            "raw_data": self.raw_data or {},
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PlatformBalance":
        """Create instance from dictionary."""
        last_updated = datetime.now()
        if "last_updated" in data:
            try:
                last_updated = datetime.fromisoformat(data["last_updated"])
            except AttributeError:
                # Python 3.6 compatibility - fromisoformat not available
                last_updated = datetime.strptime(data["last_updated"][:19], "%Y-%m-%dT%H:%M:%S")
        
        return cls(
            platform=data.get("platform", ""),
            account_id=data.get("account_id", ""),
            balance=float(data.get("balance", 0.0)),
            currency=data.get("currency", "USD"),
            usage_this_month=float(data.get("usage_this_month", 0.0)),
            usage_total=float(data.get("usage_total", 0.0)),
            last_updated=last_updated,
            status=BalanceStatus(data.get("status", "unknown")),
            raw_data=data.get("raw_data", {}),
        )
    
    def update_status(self, warning_threshold: float, critical_threshold: float) -> None:
        """
        Update the status based on balance thresholds.
        
        Args:
            warning_threshold: Balance below this triggers WARNING status.
            critical_threshold: Balance below this triggers CRITICAL status.
        """
        if self.status == BalanceStatus.ERROR:
            return
        
        if self.balance <= 0:
            self.status = BalanceStatus.ERROR
        elif self.balance < critical_threshold:
            self.status = BalanceStatus.CRITICAL
        elif self.balance < warning_threshold:
            self.status = BalanceStatus.WARNING
        else:
            self.status = BalanceStatus.ACTIVE


@dataclass
class UsageReport:
    """
    Represents usage statistics for a platform.
    
    Attributes:
        platform: Platform identifier.
        start_date: Start date of the reporting period.
        end_date: End date of the reporting period.
        total_usage: Total usage amount for the period.
        daily_usage: Daily breakdown of usage.
        currency: Currency code.
    """
    platform: str
    start_date: date
    end_date: date
    total_usage: float = 0.0
    daily_usage: Dict[str, float] = field(default_factory=dict)
    currency: str = "USD"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "platform": self.platform,
            "start_date": self.start_date.isoformat(),
            "end_date": self.end_date.isoformat(),
            "total_usage": self.total_usage,
            "daily_usage": self.daily_usage,
            "currency": self.currency,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "UsageReport":
        """Create instance from dictionary."""
        start_date = data.get("start_date")
        end_date = data.get("end_date")
        
        # Python 3.6 compatibility - fromisoformat not available
        if isinstance(start_date, str):
            start_date = date.strptime(start_date, "%Y-%m-%d")
        if isinstance(end_date, str):
            end_date = date.strptime(end_date, "%Y-%m-%d")
        
        return cls(
            platform=data.get("platform", ""),
            start_date=start_date,
            end_date=end_date,
            total_usage=float(data.get("total_usage", 0.0)),
            daily_usage=data.get("daily_usage", {}),
            currency=data.get("currency", "USD"),
        )


@dataclass
class PlatformConfig:
    """
    Configuration for a single platform.
    
    Attributes:
        name: Platform name/identifier.
        enabled: Whether this platform is enabled.
        api_key: API key for authentication (can be env var reference).
        method: Query method ('api' or 'manual').
        check_interval: How often to check balance (seconds).
        extra: Additional platform-specific configuration.
    """
    name: str
    enabled: bool = True
    api_key: Optional[str] = None
    method: str = "api"  # 'api' or 'manual'
    check_interval: int = 3600
    extra: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "name": self.name,
            "enabled": self.enabled,
            "api_key": self.api_key,
            "method": self.method,
            "check_interval": self.check_interval,
            "extra": self.extra,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PlatformConfig":
        """Create instance from dictionary."""
        return cls(
            name=data.get("name", ""),
            enabled=data.get("enabled", True),
            api_key=data.get("api_key"),
            method=data.get("method", "api"),
            check_interval=data.get("check_interval", 3600),
            extra=data.get("extra", {}),
        )


@dataclass
class SystemSummary:
    """
    Summary of all platform balances.
    
    Attributes:
        total_balance: Sum of all balances (normalized to primary currency).
        platform_count: Number of platforms configured.
        platforms_active: Number of platforms with ACTIVE status.
        platforms_warning: Number of platforms with WARNING status.
        platforms_critical: Number of platforms with CRITICAL status.
        platforms_error: Number of platforms with ERROR status.
        balances: List of individual platform balances.
        generated_at: When this summary was generated.
    """
    total_balance: float = 0.0
    platform_count: int = 0
    platforms_active: int = 0
    platforms_warning: int = 0
    platforms_critical: int = 0
    platforms_error: int = 0
    balances: List[PlatformBalance] = field(default_factory=list)
    generated_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "total_balance": self.total_balance,
            "platform_count": self.platform_count,
            "platforms_active": self.platforms_active,
            "platforms_warning": self.platforms_warning,
            "platforms_critical": self.platforms_critical,
            "platforms_error": self.platforms_error,
            "balances": [b.to_dict() for b in self.balances],
            "generated_at": self.generated_at.isoformat(),
        }
    
    def update_from_balances(self, balances: List[PlatformBalance]) -> None:
        """
        Update summary statistics from a list of balances.
        
        Args:
            balances: List of PlatformBalance objects.
        """
        self.balances = balances
        self.platform_count = len(balances)
        self.platforms_active = sum(1 for b in balances if b.status == BalanceStatus.ACTIVE)
        self.platforms_warning = sum(1 for b in balances if b.status == BalanceStatus.WARNING)
        self.platforms_critical = sum(1 for b in balances if b.status == BalanceStatus.CRITICAL)
        self.platforms_error = sum(1 for b in balances if b.status == BalanceStatus.ERROR)
        # Note: total_balance requires currency conversion which is not implemented yet
        self.total_balance = sum(b.balance for b in balances if b.currency == "USD")
