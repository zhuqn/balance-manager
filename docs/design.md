# Balance Management System - Design Specification

## 1. Overview

A Python-based system for managing third-party service balances and usage across multiple AI/ML platforms.

## 2. System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Balance Management System                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   CLI/TUI    │  │  Web Dashboard│  │  API Server  │          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
│         │                 │                 │                   │
│         └─────────────────┼─────────────────┘                   │
│                           │                                     │
│                  ┌────────▼────────┐                            │
│                  │  BalanceManager │                            │
│                  │  (Core Logic)   │                            │
│                  └────────┬────────┘                            │
│                           │                                     │
│         ┌─────────────────┼─────────────────┐                   │
│         │                 │                 │                   │
│  ┌──────▼───────┐  ┌──────▼───────┐  ┌──────▼───────┐          │
│  │ API Providers│  │ Manual Entry │  │ Data Storage │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## 3. Platform Support Matrix

| Platform | API Available | Implementation | Priority |
|----------|---------------|----------------|----------|
| OpenRouter | ✅ Yes | REST API | High |
| MiniMax (海螺 AI) | ✅ Yes | REST API | High |
| Volcengine (火山方舟) | ✅ Yes | REST API | High |
| BFL (Kontext) | ✅ Yes | REST API | Medium |
| Aliyun (悠船) | ❌ No | Browser/Selenium | Medium |
| Kling AI (可灵) | ❌ No | Manual Entry | Medium |
| PixVerse | ❌ No | Manual Entry | Low |
| MiracleVision (美图) | ❌ No | Manual Entry | Low |

## 4. Data Models

### 4.1 Platform Balance

```python
@dataclass
class PlatformBalance:
    platform: str           # Platform identifier
    account_id: str         # Account identifier
    balance: float          # Current balance
    currency: str           # Currency code (USD, CNY, etc.)
    usage_this_month: float # Usage this month
    usage_total: float      # Total usage
    last_updated: datetime  # Last update timestamp
    status: BalanceStatus   # active, warning, critical, unknown
```

### 4.2 Balance Status Enum

```python
class BalanceStatus(Enum):
    ACTIVE = "active"           # Normal
    WARNING = "warning"         # Below threshold
    CRITICAL = "critical"       # Critically low
    UNKNOWN = "unknown"         # Unable to fetch
    ERROR = "error"             # Fetch error
```

### 4.3 Provider Interface

```python
class BalanceProvider(ABC):
    @abstractmethod
    async def get_balance(self) -> PlatformBalance:
        pass
    
    @abstractmethod
    async def get_usage(self, start_date: date, end_date: date) -> UsageReport:
        pass
    
    @property
    @abstractmethod
    def platform_name(self) -> str:
        pass
```

## 5. Module Structure

```
src/
├── __init__.py
├── main.py                 # Entry point
├── core/
│   ├── __init__.py
│   ├── manager.py          # BalanceManager
│   ├── models.py           # Data models
│   └── exceptions.py       # Custom exceptions
├── providers/
│   ├── __init__.py
│   ├── base.py             # Base provider class
│   ├── openrouter.py       # OpenRouter API
│   ├── minimax.py          # MiniMax API
│   ├── volcengine.py       # Volcengine API
│   ├── bfl.py              # BFL/Kontext API
│   └── manual.py           # Manual entry provider
├── storage/
│   ├── __init__.py
│   ├── json_store.py       # JSON file storage
│   └── base.py             # Storage interface
├── cli/
│   ├── __init__.py
│   └── main.py             # CLI interface
└── config/
    ├── __init__.py
    └── settings.py         # Configuration management
```

## 6. API Specifications

### 6.1 OpenRouter API

```
GET https://openrouter.ai/api/v1/auth/key
Headers: Authorization: Bearer {API_KEY}
Response: { "data": { "limit": "...", "usage": "..." } }
```

### 6.2 MiniMax API

```
POST https://api.minimaxi.com/v1/balance/query
Headers: Authorization: Bearer {API_KEY}
Response: { "balance": 123.45, "currency": "CNY" }
```

### 6.3 Volcengine API

```
POST https://ark.cn-beijing.volces.com/api/v3/balance
Headers: Authorization: Bearer {API_KEY}
Response: { "available_balance": "...", "total_balance": "..." }
```

## 7. Configuration

### 7.1 Config File (~/.balance_manager/config.yaml)

```yaml
platforms:
  openrouter:
    enabled: true
    api_key: "${OPENROUTER_API_KEY}"
    check_interval: 3600  # seconds
    
  minimax:
    enabled: true
    api_key: "${MINIMAX_API_KEY}"
    
  volcengine:
    enabled: true
    api_key: "${VOLCENGINE_API_KEY}"
    
  bfl:
    enabled: true
    api_key: "${BFL_API_KEY}"

  # Manual entry platforms
  aliyun:
    enabled: true
    method: manual
    
  kling:
    enabled: true
    method: manual

thresholds:
  warning: 100.0    # Warn when balance below this
  critical: 50.0    # Critical alert below this

storage:
  type: json
  path: ~/.balance_manager/data.json
```

## 8. CLI Commands

```bash
# Check all balances
balance-manager check

# Check specific platform
balance-manager check --platform openrouter

# Manual entry
balance-manager enter --platform aliyun --balance 500.00

# View summary
balance-manager summary

# Export report
balance-manager export --format csv

# Configure thresholds
balance-manager config --warning 100 --critical 50
```

## 9. Error Handling

| Error Type | Handling |
|------------|----------|
| API Key Invalid | Log error, mark status=ERROR, continue |
| Network Timeout | Retry 3 times with backoff, then ERROR |
| Rate Limit | Wait and retry, log warning |
| Parse Error | Log details, mark UNKNOWN |
| Storage Error | Fallback to memory, alert user |

## 10. Security Considerations

- API keys stored in environment variables or encrypted config
- No keys logged or printed
- HTTPS for all API calls
- Input validation for manual entries

## 11. Testing Strategy

### Unit Tests
- Provider implementations
- Data model serialization
- Configuration parsing
- Error handling paths

### Integration Tests
- API provider connectivity (mocked)
- Storage read/write
- CLI command execution

### Test Coverage Goal: >80%
