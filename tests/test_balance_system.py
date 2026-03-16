"""
Unit tests for the balance management system.

Synchronous version for Python 3.6 compatibility.
"""

import pytest
import json
from datetime import datetime, date
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.models import (
    PlatformBalance,
    BalanceStatus,
    UsageReport,
    PlatformConfig,
    SystemSummary,
)
from core.exceptions import (
    BalanceError,
    ProviderError,
    ConfigurationError,
    StorageError,
    AuthenticationError,
    RateLimitError,
    ManualEntryRequired,
)
from core.manager import BalanceManager
from providers.base import BalanceProvider
from providers.manual import ManualProvider


# =============================================================================
# Model Tests
# =============================================================================

class TestPlatformBalance:
    """Tests for PlatformBalance model."""
    
    def test_create_balance(self):
        """Test creating a PlatformBalance instance."""
        balance = PlatformBalance(
            platform="openrouter",
            balance=100.0,
            currency="USD",
        )
        
        assert balance.platform == "openrouter"
        assert balance.balance == 100.0
        assert balance.currency == "USD"
        assert balance.status == BalanceStatus.UNKNOWN
    
    def test_balance_to_dict(self):
        """Test serialization to dictionary."""
        balance = PlatformBalance(
            platform="minimax",
            balance=50.0,
            currency="CNY",
        )
        
        data = balance.to_dict()
        
        assert data["platform"] == "minimax"
        assert data["balance"] == 50.0
        assert data["currency"] == "CNY"
        assert "last_updated" in data
        assert "status" in data
    
    def test_balance_from_dict(self):
        """Test deserialization from dictionary."""
        data = {
            "platform": "volcengine",
            "balance": 200.0,
            "currency": "CNY",
            "status": "active",
            "last_updated": "2026-03-10T20:00:00",
        }
        
        balance = PlatformBalance.from_dict(data)
        
        assert balance.platform == "volcengine"
        assert balance.balance == 200.0
        assert balance.status == BalanceStatus.ACTIVE
    
    def test_update_status_active(self):
        """Test status update when balance is healthy."""
        balance = PlatformBalance(platform="test", balance=150.0)
        balance.update_status(warning_threshold=100.0, critical_threshold=50.0)
        
        assert balance.status == BalanceStatus.ACTIVE
    
    def test_update_status_warning(self):
        """Test status update when balance is below warning."""
        balance = PlatformBalance(platform="test", balance=75.0)
        balance.update_status(warning_threshold=100.0, critical_threshold=50.0)
        
        assert balance.status == BalanceStatus.WARNING
    
    def test_update_status_critical(self):
        """Test status update when balance is critical."""
        balance = PlatformBalance(platform="test", balance=25.0)
        balance.update_status(warning_threshold=100.0, critical_threshold=50.0)
        
        assert balance.status == BalanceStatus.CRITICAL
    
    def test_update_status_error_not_changed(self):
        """Test that ERROR status is not changed by update."""
        balance = PlatformBalance(platform="test", balance=100.0, status=BalanceStatus.ERROR)
        balance.update_status(warning_threshold=100.0, critical_threshold=50.0)
        
        assert balance.status == BalanceStatus.ERROR


class TestUsageReport:
    """Tests for UsageReport model."""
    
    def test_create_usage_report(self):
        """Test creating a UsageReport instance."""
        report = UsageReport(
            platform="openrouter",
            start_date=date(2026, 3, 1),
            end_date=date(2026, 3, 31),
            total_usage=50.0,
        )
        
        assert report.platform == "openrouter"
        assert report.total_usage == 50.0
    
    def test_usage_report_to_dict(self):
        """Test serialization to dictionary."""
        report = UsageReport(
            platform="test",
            start_date=date(2026, 3, 1),
            end_date=date(2026, 3, 31),
        )
        
        data = report.to_dict()
        
        assert data["start_date"] == "2026-03-01"
        assert data["end_date"] == "2026-03-31"


class TestSystemSummary:
    """Tests for SystemSummary model."""
    
    def test_create_summary(self):
        """Test creating a SystemSummary instance."""
        summary = SystemSummary()
        
        assert summary.total_balance == 0.0
        assert summary.platform_count == 0
    
    def test_update_from_balances(self):
        """Test updating summary from balances."""
        balances = [
            PlatformBalance(platform="p1", balance=100.0, status=BalanceStatus.ACTIVE),
            PlatformBalance(platform="p2", balance=75.0, status=BalanceStatus.WARNING),
            PlatformBalance(platform="p3", balance=25.0, status=BalanceStatus.CRITICAL),
        ]
        
        summary = SystemSummary()
        summary.update_from_balances(balances)
        
        assert summary.platform_count == 3
        assert summary.platforms_active == 1
        assert summary.platforms_warning == 1
        assert summary.platforms_critical == 1


# =============================================================================
# Exception Tests
# =============================================================================

class TestExceptions:
    """Tests for custom exceptions."""
    
    def test_provider_error(self):
        """Test ProviderError exception."""
        error = ProviderError("openrouter", "API error")
        
        assert "openrouter" in str(error)
        assert "API error" in str(error)
    
    def test_authentication_error(self):
        """Test AuthenticationError exception."""
        error = AuthenticationError("minimax", "Invalid key")
        
        assert isinstance(error, ProviderError)
        assert error.platform == "minimax"
    
    def test_rate_limit_error_with_retry(self):
        """Test RateLimitError with retry_after."""
        error = RateLimitError("volcengine", "Too many requests", retry_after=60)
        
        assert error.retry_after == 60
    
    def test_manual_entry_required(self):
        """Test ManualEntryRequired exception."""
        error = ManualEntryRequired("aliyun")
        
        assert "aliyun" in str(error)


# =============================================================================
# Provider Tests
# =============================================================================

class TestManualProvider:
    """Tests for ManualProvider."""
    
    def test_create_manual_provider(self):
        """Test creating ManualProvider."""
        provider = ManualProvider(platform_name="aliyun")
        
        assert provider.platform_name == "aliyun"
    
    def test_set_balance(self):
        """Test setting balance manually."""
        provider = ManualProvider(platform_name="test", stored_balance=100.0)
        
        balance = provider.get_last_balance()
        
        assert balance is not None
        assert balance.balance == 100.0
    
    def test_get_balance_raises_manual_entry(self):
        """Test that get_balance raises ManualEntryRequired when no stored balance."""
        provider = ManualProvider(platform_name="test")
        
        with pytest.raises(ManualEntryRequired):
            provider.get_balance()


class TestMockProvider(BalanceProvider):
    """Mock provider for testing."""
    
    @property
    def platform_name(self) -> str:
        return "mock"
    
    def get_balance(self) -> PlatformBalance:
        return PlatformBalance(
            platform=self.platform_name,
            balance=100.0,
            status=BalanceStatus.ACTIVE,
        )
    
    def get_usage(self, start_date: date, end_date: date) -> UsageReport:
        return UsageReport(
            platform=self.platform_name,
            start_date=start_date,
            end_date=end_date,
        )


# =============================================================================
# Manager Tests
# =============================================================================

class TestBalanceManager:
    """Tests for BalanceManager."""
    
    def test_create_manager(self):
        """Test creating BalanceManager."""
        manager = BalanceManager(
            warning_threshold=100.0,
            critical_threshold=50.0,
        )
        
        assert manager.warning_threshold == 100.0
        assert manager.critical_threshold == 50.0
    
    def test_register_provider(self):
        """Test registering a provider."""
        manager = BalanceManager()
        provider = TestMockProvider()
        config = PlatformConfig(name="mock", enabled=True)
        
        manager.register_provider(provider, config)
        
        assert "mock" in manager.providers
        assert manager.get_platform_names() == ["mock"]
    
    def test_register_disabled_provider(self):
        """Test that disabled providers are not registered."""
        manager = BalanceManager()
        provider = TestMockProvider()
        config = PlatformConfig(name="mock", enabled=False)
        
        manager.register_provider(provider, config)
        
        assert "mock" not in manager.providers
    
    def test_check_single_balance(self):
        """Test checking a single balance."""
        manager = BalanceManager()
        provider = TestMockProvider()
        config = PlatformConfig(name="mock", enabled=True)
        
        manager.register_provider(provider, config)
        
        balance = manager.check_balance("mock")
        assert balance.platform == "mock"
        assert balance.balance == 100.0
    
    def test_check_all_balances(self):
        """Test checking all balances."""
        manager = BalanceManager()
        
        for name in ["p1", "p2"]:
            provider = TestMockProvider()
            config = PlatformConfig(name=name, enabled=True)
            manager.register_provider(provider, config)
        
        balances = manager.check_all_balances()
        assert len(balances) == 2
    
    def test_get_summary(self):
        """Test generating summary."""
        manager = BalanceManager()
        
        balances = [
            PlatformBalance(platform="p1", balance=100.0, status=BalanceStatus.ACTIVE),
        ]
        
        summary = manager.get_summary(balances)
        
        assert summary.platform_count == 1
        assert isinstance(summary.generated_at, datetime)
    
    def test_check_and_summarize(self):
        """Test combined check and summarize."""
        manager = BalanceManager()
        provider = TestMockProvider()
        config = PlatformConfig(name="mock", enabled=True)
        manager.register_provider(provider, config)
        
        summary = manager.check_and_summarize()
        assert summary.platform_count == 1


# =============================================================================
# Configuration Tests
# =============================================================================

class TestConfiguration:
    """Tests for configuration management."""
    
    def test_config_from_dict(self):
        """Test creating Config from dictionary."""
        from config.settings import Config
        
        data = {
            "thresholds": {
                "warning": 200.0,
                "critical": 100.0,
            },
            "platforms": {
                "openrouter": {
                    "enabled": True,
                    "api_key": "${OPENROUTER_API_KEY}",
                }
            }
        }
        
        config = Config.from_dict(data)
        
        assert config.thresholds.warning == 200.0
        assert config.thresholds.critical == 100.0
        assert "openrouter" in config.platforms
    
    def test_env_var_resolution(self):
        """Test environment variable resolution in config."""
        from config.settings import Config
        import os
        
        os.environ["TEST_API_KEY"] = "secret123"
        
        value = Config._resolve_env_var("${TEST_API_KEY}")
        
        assert value == "secret123"
        
        del os.environ["TEST_API_KEY"]
    
    def test_config_to_dict(self):
        """Test converting Config to dictionary."""
        from config.settings import Config
        
        config = Config()
        data = config.to_dict()
        
        assert "thresholds" in data
        assert "platforms" in data
        assert "storage" in data


# =============================================================================
# Integration Tests
# =============================================================================

class TestIntegration:
    """Integration tests for the system."""
    
    def test_full_workflow(self):
        """Test complete workflow: register, check, summarize."""
        manager = BalanceManager(
            warning_threshold=100.0,
            critical_threshold=50.0,
        )
        
        # Register providers
        for name in ["p1", "p2", "p3"]:
            provider = TestMockProvider()
            config = PlatformConfig(name=name, enabled=True)
            manager.register_provider(provider, config)
        
        # Check all
        summary = manager.check_and_summarize()
        
        # Verify
        assert summary.platform_count == 3
        assert summary.platforms_active == 3
        assert summary.platforms_warning == 0
        assert summary.platforms_critical == 0


# =============================================================================
# Run Tests
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
