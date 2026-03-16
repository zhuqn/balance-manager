import { useState } from 'react';
import type { PlatformBalance } from '../types';
import { StatusBadge } from './StatusBadge';

interface PlatformCardProps {
  balance: PlatformBalance;
  onRefresh: (platformName: string) => Promise<void>;
  onEnterBalance: (platformName: string) => void;
}

export function PlatformCard({ balance, onRefresh, onEnterBalance }: PlatformCardProps) {
  const [refreshing, setRefreshing] = useState(false);

  const handleRefresh = async () => {
    setRefreshing(true);
    try {
      await onRefresh(balance.platform);
    } finally {
      setRefreshing(false);
    }
  };

  const formatCurrency = (amount: number, currency: string) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: currency,
      minimumFractionDigits: 2,
    }).format(amount);
  };

  const formatLastUpdated = (isoString: string) => {
    const date = new Date(isoString);
    return date.toLocaleString();
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
      <div className="flex items-start justify-between mb-4">
        <div>
          <h3 className="text-lg font-semibold text-gray-900 capitalize">
            {balance.platform.replace(/-/g, ' ')}
          </h3>
          {balance.account_id && (
            <p className="text-sm text-gray-500">{balance.account_id}</p>
          )}
        </div>
        <StatusBadge status={balance.status} />
      </div>

      <div className="mb-4">
        <p className="text-3xl font-bold text-gray-900">
          {formatCurrency(balance.balance, balance.currency)}
        </p>
        <p className="text-sm text-gray-500">{balance.currency}</p>
      </div>

      {balance.usage_this_month > 0 && (
        <div className="mb-4 p-3 bg-gray-50 rounded-md">
          <p className="text-sm text-gray-600">Usage This Month</p>
          <p className="text-lg font-medium text-gray-900">
            {formatCurrency(balance.usage_this_month, balance.currency)}
          </p>
        </div>
      )}

      <div className="flex items-center justify-between text-sm text-gray-500 mb-4">
        <span>Updated: {formatLastUpdated(balance.last_updated)}</span>
      </div>

      <div className="flex gap-2">
        <button
          onClick={handleRefresh}
          disabled={refreshing}
          className="flex-1 px-4 py-2 bg-primary-500 text-white rounded-md hover:bg-primary-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {refreshing ? 'Refreshing...' : 'Refresh'}
        </button>
        <button
          onClick={() => onEnterBalance(balance.platform)}
          className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50 transition-colors"
        >
          Enter Balance
        </button>
      </div>
    </div>
  );
}
