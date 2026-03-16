export interface PlatformBalance {
  platform: string;
  account_id: string;
  balance: number;
  currency: string;
  usage_this_month: number;
  usage_total: number;
  last_updated: string;
  status: BalanceStatus;
  raw_data: Record<string, any>;
}

export type BalanceStatus = 'active' | 'warning' | 'critical' | 'unknown' | 'error';

export interface SystemSummary {
  total_balance: number;
  platform_count: number;
  platforms_active: number;
  platforms_warning: number;
  platforms_critical: number;
  platforms_error: number;
  balances: PlatformBalance[];
  generated_at: string;
}

export interface PlatformConfig {
  name: string;
  enabled: boolean;
  method: 'api' | 'manual';
  has_api_key: boolean;
}

export interface ConfigResponse {
  thresholds: {
    warning: number;
    critical: number;
  };
  platforms: Record<string, any>;
  storage: {
    type: string;
    path: string;
  };
}

export interface HistoryEntry {
  date: string;
  balance: number;
  status: BalanceStatus;
}

export interface PlatformHistory {
  platform: string;
  days: number;
  history: HistoryEntry[];
}
