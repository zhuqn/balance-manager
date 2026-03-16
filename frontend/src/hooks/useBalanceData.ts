import { useState, useEffect, useCallback } from 'react';
import { api } from '../api/client';
import type { SystemSummary, PlatformBalance } from '../types';

interface UseBalanceDataReturn {
  summary: SystemSummary | null;
  loading: boolean;
  error: string | null;
  refresh: () => Promise<void>;
  refreshPlatform: (platformName: string) => Promise<PlatformBalance | null>;
}

export function useBalanceData(): UseBalanceDataReturn {
  const [summary, setSummary] = useState<SystemSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(async (refresh = false) => {
    try {
      setLoading(true);
      setError(null);
      const data = await api.getSummary(refresh);
      setSummary(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch data');
    } finally {
      setLoading(false);
    }
  }, []);

  const refreshPlatform = useCallback(async (platformName: string): Promise<PlatformBalance | null> => {
    try {
      const balance = await api.checkPlatformBalance(platformName);
      // Update local summary
      setSummary(prev => {
        if (!prev) return prev;
        const newBalances = prev.balances.map(b => 
          b.platform === platformName ? balance : b
        );
        return {
          ...prev,
          balances: newBalances,
          generated_at: new Date().toISOString(),
        };
      });
      return balance;
    } catch (err) {
      console.error(`Failed to refresh ${platformName}:`, err);
      return null;
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return {
    summary,
    loading,
    error,
    refresh: () => fetchData(true),
    refreshPlatform,
  };
}
