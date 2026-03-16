import type { SystemSummary, PlatformBalance, PlatformConfig, ConfigResponse, PlatformHistory } from '../types';

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail || 'Request failed');
  }
  return response.json();
}

export const api = {
  async getSummary(refresh = false): Promise<SystemSummary> {
    const response = await fetch(`${API_BASE}/api/summary?refresh=${refresh}`);
    return handleResponse<SystemSummary>(response);
  },

  async getPlatforms(): Promise<PlatformConfig[]> {
    const response = await fetch(`${API_BASE}/api/platforms`);
    const data = await handleResponse<{ platforms: PlatformConfig[] }>(response);
    return data.platforms;
  },

  async getPlatformBalance(platformName: string, refresh = false): Promise<PlatformBalance> {
    const response = await fetch(`${API_BASE}/api/platform/${platformName}?refresh=${refresh}`);
    return handleResponse<PlatformBalance>(response);
  },

  async checkPlatformBalance(platformName: string): Promise<PlatformBalance> {
    const response = await fetch(`${API_BASE}/api/platform/${platformName}/check`, {
      method: 'POST',
    });
    return handleResponse<PlatformBalance>(response);
  },

  async enterManualBalance(
    platformName: string,
    balance: number,
    currency: string
  ): Promise<PlatformBalance> {
    const response = await fetch(`${API_BASE}/api/platform/${platformName}/balance`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ balance, currency }),
    });
    return handleResponse<PlatformBalance>(response);
  },

  async getHistory(platformName: string, days = 30): Promise<PlatformHistory> {
    const response = await fetch(`${API_BASE}/api/history/${platformName}?days=${days}`);
    return handleResponse<PlatformHistory>(response);
  },

  async getConfig(): Promise<ConfigResponse> {
    const response = await fetch(`${API_BASE}/api/config`);
    return handleResponse<ConfigResponse>(response);
  },

  async updateThresholds(warning?: number, critical?: number): Promise<ConfigResponse> {
    const response = await fetch(`${API_BASE}/api/config/thresholds`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ warning_threshold: warning, critical_threshold: critical }),
    });
    return handleResponse<ConfigResponse>(response);
  },

  async healthCheck(): Promise<{ status: string; version: string; timestamp: string }> {
    const response = await fetch(`${API_BASE}/health`);
    return handleResponse(response);
  },
};
