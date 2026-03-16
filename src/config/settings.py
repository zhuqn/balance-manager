"""
Configuration settings management.

Loads configuration from YAML file with environment variable substitution.
"""

import os
import re
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field

# Import with fallback for direct module execution
try:
    from core.models import PlatformConfig
    from core.exceptions import ConfigurationError
except ImportError:
    from ..core.models import PlatformConfig
    from ..core.exceptions import ConfigurationError


@dataclass
class ThresholdConfig:
    """Threshold configuration for balance alerts."""
    warning: float = 100.0
    critical: float = 50.0


@dataclass
class StorageConfig:
    """Storage configuration."""
    type: str = "json"
    path: str = "~/.balance_manager/data.json"


@dataclass
class Config:
    """
    Main configuration class.
    
    Attributes:
        platforms: Platform-specific configurations.
        thresholds: Alert threshold settings.
        storage: Storage backend settings.
    """
    platforms: Dict[str, PlatformConfig] = field(default_factory=dict)
    thresholds: ThresholdConfig = field(default_factory=ThresholdConfig)
    storage: StorageConfig = field(default_factory=StorageConfig)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Config":
        """
        Create Config from dictionary.
        
        Args:
            data: Configuration dictionary.
            
        Returns:
            Config instance.
        """
        config = cls()
        
        # Parse platforms
        platforms_data = data.get("platforms", {})
        for name, platform_data in platforms_data.items():
            config.platforms[name] = PlatformConfig(
                name=name,
                enabled=platform_data.get("enabled", True),
                api_key=cls._resolve_env_var(platform_data.get("api_key")),
                method=platform_data.get("method", "api"),
                check_interval=platform_data.get("check_interval", 3600),
                extra=platform_data.get("extra", {}),
            )
        
        # Parse thresholds
        thresholds_data = data.get("thresholds", {})
        config.thresholds = ThresholdConfig(
            warning=float(thresholds_data.get("warning", 100.0)),
            critical=float(thresholds_data.get("critical", 50.0)),
        )
        
        # Parse storage
        storage_data = data.get("storage", {})
        config.storage = StorageConfig(
            type=storage_data.get("type", "json"),
            path=storage_data.get("path", "~/.balance_manager/data.json"),
        )
        
        return config
    
    @staticmethod
    def _resolve_env_var(value: Optional[str]) -> Optional[str]:
        """
        Resolve environment variable references.
        
        Supports ${VAR_NAME} or $VAR_NAME syntax.
        
        Args:
            value: Value that may contain env var references.
            
        Returns:
            Resolved value.
        """
        if not value:
            return None
        
        # Match ${VAR_NAME} pattern
        pattern = r'\$\{([^}]+)\}'
        
        def replace(match):
            env_var = match.group(1)
            return os.environ.get(env_var, "")
        
        return re.sub(pattern, replace, value)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert Config to dictionary."""
        return {
            "platforms": {
                name: config.to_dict() for name, config in self.platforms.items()
            },
            "thresholds": {
                "warning": self.thresholds.warning,
                "critical": self.thresholds.critical,
            },
            "storage": {
                "type": self.storage.type,
                "path": self.storage.path,
            },
        }
    
    def get_enabled_platforms(self) -> List[PlatformConfig]:
        """Get list of enabled platform configurations."""
        return [p for p in self.platforms.values() if p.enabled]
    
    def get_api_platforms(self) -> List[PlatformConfig]:
        """Get platforms with API method."""
        return [p for p in self.platforms.values() if p.method == "api" and p.enabled]
    
    def get_manual_platforms(self) -> List[PlatformConfig]:
        """Get platforms with manual method."""
        return [p for p in self.platforms.values() if p.method == "manual" and p.enabled]


def get_config_path() -> Path:
    """Get the default configuration file path."""
    return Path.home() / ".balance_manager" / "config.yaml"


def load_config(config_path: Optional[str] = None) -> Config:
    """
    Load configuration from YAML file.
    
    Args:
        config_path: Optional path to config file.
        
    Returns:
        Config instance.
    """
    import yaml
    
    path = Path(config_path) if config_path else get_config_path()
    
    if not path.exists():
        # Return default config if file doesn't exist
        return Config()
    
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f) or {}
        return Config.from_dict(data)
    except yaml.YAMLError as e:
        raise ConfigurationError("config.yaml", f"Invalid YAML: {str(e)}")
    except IOError as e:
        raise ConfigurationError("config.yaml", f"Cannot read file: {str(e)}")


def save_config(config: Config, config_path: Optional[str] = None) -> None:
    """
    Save configuration to YAML file.
    
    Args:
        config: Config instance to save.
        config_path: Optional path to config file.
    """
    import yaml
    
    path = Path(config_path) if config_path else get_config_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(path, 'w', encoding='utf-8') as f:
        yaml.safe_dump(config.to_dict(), f, default_flow_style=False, allow_unicode=True)


def create_default_config() -> Config:
    """
    Create a default configuration with all supported platforms.
    
    Returns:
        Config with default platform settings.
    """
    config = Config()
    
    # API platforms
    api_platforms = [
        ("openrouter", "OpenRouter", "${OPENROUTER_API_KEY}"),
        ("minimax", "MiniMax (海螺 AI)", "${MINIMAX_API_KEY}"),
        ("volcengine", "Volcengine (火山方舟)", "${VOLCENGINE_API_KEY}"),
        ("bfl", "BFL (Kontext)", "${BFL_API_KEY}"),
    ]
    
    for name, _, api_key_template in api_platforms:
        config.platforms[name] = PlatformConfig(
            name=name,
            enabled=True,
            api_key=api_key_template,
            method="api",
        )
    
    # Manual platforms
    manual_platforms = [
        ("aliyun", "Aliyun (悠船)"),
        ("kling", "Kling AI (可灵)"),
        ("pixverse", "PixVerse"),
        ("miracle", "MiracleVision (美图)"),
    ]
    
    for name, _ in manual_platforms:
        config.platforms[name] = PlatformConfig(
            name=name,
            enabled=True,
            method="manual",
        )
    
    return config
