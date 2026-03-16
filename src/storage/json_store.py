"""
JSON file storage backend.

Synchronous version for Python 3.6 compatibility.
"""

import json
import threading
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

# Import with fallback for direct module execution
try:
    from .base import StorageBackend
    from core.models import PlatformBalance, SystemSummary
    from core.exceptions import StorageError
except ImportError:
    from ..core.models import PlatformBalance, SystemSummary
    from ..core.exceptions import StorageError
    from .base import StorageBackend


class JSONStorage(StorageBackend):
    """JSON file-based storage backend."""
    
    def __init__(self, file_path: str):
        """Initialize JSON storage."""
        self.file_path = Path(file_path)
        self._lock = threading.Lock()
    
    def _ensure_file(self) -> None:
        """Ensure the data file exists."""
        if not self.file_path.exists():
            self.file_path.parent.mkdir(parents=True, exist_ok=True)
            initial_data = {
                "version": "1.0",
                "last_updated": None,
                "balances": [],
                "summaries": [],
            }
            self._write_data(initial_data)
    
    def _read_data(self) -> Dict[str, Any]:
        """Read data from the JSON file."""
        try:
            if not self.file_path.exists():
                return {
                    "version": "1.0",
                    "last_updated": None,
                    "balances": [],
                    "summaries": [],
                }
            
            with open(self.file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                return json.loads(content) if content else {}
        except json.JSONDecodeError as e:
            raise StorageError("read", str(self.file_path), f"Invalid JSON: {str(e)}")
        except IOError as e:
            raise StorageError("read", str(self.file_path), str(e))
    
    def _write_data(self, data: Dict[str, Any]) -> None:
        """Write data to the JSON file."""
        try:
            with open(self.file_path, 'w', encoding='utf-8') as f:
                f.write(json.dumps(data, indent=2, ensure_ascii=False))
        except IOError as e:
            raise StorageError("write", str(self.file_path), str(e))
    
    def save_balances(self, balances: List[PlatformBalance]) -> None:
        """Save balances to the JSON file."""
        with self._lock:
            self._ensure_file()
            data = self._read_data()
            
            data["balances"] = [b.to_dict() for b in balances]
            data["last_updated"] = datetime.now().isoformat()
            
            self._write_data(data)
    
    def load_balances(self) -> List[PlatformBalance]:
        """Load balances from the JSON file."""
        with self._lock:
            self._ensure_file()
            data = self._read_data()
            
            balances_data = data.get("balances", [])
            return [PlatformBalance.from_dict(b) for b in balances_data]
    
    def save_summary(self, summary: SystemSummary) -> None:
        """Save a system summary to history."""
        with self._lock:
            self._ensure_file()
            data = self._read_data()
            
            if "summaries" not in data:
                data["summaries"] = []
            
            data["summaries"].append(summary.to_dict())
            
            # Keep only last 90 days
            cutoff = datetime.now() - timedelta(days=90)
            data["summaries"] = [
                s for s in data["summaries"]
                if self._parse_datetime(s.get("generated_at", "")) > cutoff
            ]
            
            self._write_data(data)
    
    def load_history(self, days: int = 30) -> List[SystemSummary]:
        """Load summary history."""
        with self._lock:
            self._ensure_file()
            data = self._read_data()
            
            summaries_data = data.get("summaries", [])
            cutoff = datetime.now() - timedelta(days=days)
            
            filtered = [
                s for s in summaries_data
                if self._parse_datetime(s.get("generated_at", "")) > cutoff
            ]
            
            return [self._dict_to_summary(s) for s in filtered]
    
    def _parse_datetime(self, iso_string: str) -> datetime:
        """Parse ISO format datetime string (Python 3.6 compatible)."""
        if not iso_string:
            return datetime.now()
        try:
            return datetime.fromisoformat(iso_string)
        except AttributeError:
            # Python 3.6 compatibility
            return datetime.strptime(iso_string[:19], "%Y-%m-%dT%H:%M:%S")
    
    def _dict_to_summary(self, data: Dict[str, Any]) -> SystemSummary:
        """Convert dictionary to SystemSummary."""
        generated_at = datetime.now()
        if "generated_at" in data:
            generated_at = self._parse_datetime(data["generated_at"])
        
        summary = SystemSummary(
            total_balance=data.get("total_balance", 0.0),
            platform_count=data.get("platform_count", 0),
            platforms_active=data.get("platforms_active", 0),
            platforms_warning=data.get("platforms_warning", 0),
            platforms_critical=data.get("platforms_critical", 0),
            platforms_error=data.get("platforms_error", 0),
            generated_at=generated_at,
        )
        
        balances_data = data.get("balances", [])
        summary.balances = [PlatformBalance.from_dict(b) for b in balances_data]
        summary.update_from_balances(summary.balances)
        
        return summary
    
    def close(self) -> None:
        """Close storage (no-op for JSON file storage)."""
        pass
