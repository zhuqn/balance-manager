# Frontend Development Plan

## Architecture

```
balance-manager/
├── backend/              # FastAPI server
│   ├── main.py          # API entry point
│   ├── api/             # API routes
│   └── services/        # Business logic
├── frontend/            # React + TypeScript
│   ├── src/
│   │   ├── components/  # UI components
│   │   ├── pages/       # Page components
│   │   ├── hooks/       # Custom hooks
│   │   ├── api/         # API client
│   │   └── types/       # TypeScript types
│   └── public/
└── src/                 # Existing CLI code (shared)
```

## Features

### 1. Dashboard
- Total balance overview
- Platform status cards (Active/Warning/Critical/Error)
- Quick actions (Refresh all, Enter balance)

### 2. Platform Cards
- Individual platform balance display
- Status indicators with color coding
- Last updated timestamp
- Usage charts (if available)

### 3. Manual Entry Modal
- Platform selection
- Balance amount input
- Currency selection
- Submit/Cancel actions

### 4. History & Trends
- Balance history charts per platform
- Usage trends over time
- Date range selector

### 5. Settings
- Threshold configuration (warning/critical)
- API key management
- Refresh interval settings

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/summary` | Get all balances summary |
| GET | `/api/platforms` | List configured platforms |
| GET | `/api/platform/:name` | Get specific platform balance |
| POST | `/api/platform/:name/check` | Trigger balance check |
| POST | `/api/platform/:name/balance` | Manual balance entry |
| GET | `/api/history/:name` | Get balance history |
| GET | `/api/config` | Get configuration |
| PUT | `/api/config` | Update configuration |

## UI Components

- `Dashboard` - Main overview page
- `PlatformCard` - Individual platform display
- `StatusBadge` - Status indicator (Active/Warning/Critical/Error)
- `BalanceChart` - Historical balance visualization
- `ManualEntryModal` - Balance entry form
- `SettingsPanel` - Configuration UI
- `Navbar` - Navigation and global actions
- `RefreshButton` - Manual refresh trigger

## Color Scheme

- Active: Green (#10B981)
- Warning: Yellow (#F59E0B)
- Critical: Red (#EF4444)
- Error: Gray (#6B7280)
- Primary: Blue (#3B82F6)
