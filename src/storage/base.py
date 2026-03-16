"""
Storage backend interface.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime

# Import with fallback for direct module execution
try:
    from core.models import PlatformBalance, SystemSummary
except ImportError:
    from ..core.models import PlatformBalance, SystemSummary


class StorageBackend(ABC):
    """
    Abstract base class for storage backends.
    
    Subclasses implement persistent storage for balance data.
    """
    
    @abstractmethod
    def save_balances(self, balances: List[PlatformBalance]) -> None:
        """
        Save a list of platform balances.
        
        Args:
            balances: List of PlatformBalance objects to save.
        """
        pass
    
    @abstractmethod
    def load_balances(self) -> List[PlatformBalance]:
        """
        Load previously saved balances.
        
        Returns:
            List of PlatformBalance objects.
        """
        pass
    
    @abstractmethod
    def save_summary(self, summary: SystemSummary) -> None:
        """
        Save a system summary.
        
        Args:
            summary: SystemSummary to save.
        """
        pass
    
    @abstractmethod
    def load_history(self, days: int = 30) -> List[SystemSummary]:
        """
        Load summary history.
        
        Args:
            days: Number of days of history to load.
            
        Returns:
            List of SystemSummary objects.
        """
        pass
    
    @abstractmethod
    def close(self) -> None:
        """Close any open resources."""
        pass
