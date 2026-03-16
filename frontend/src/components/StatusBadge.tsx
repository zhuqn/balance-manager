import type { BalanceStatus } from '../types';

interface StatusBadgeProps {
  status: BalanceStatus;
}

const statusConfig: Record<BalanceStatus, { label: string; className: string }> = {
  active: { label: 'Active', className: 'bg-green-100 text-green-800' },
  warning: { label: 'Warning', className: 'bg-yellow-100 text-yellow-800' },
  critical: { label: 'Critical', className: 'bg-red-100 text-red-800' },
  unknown: { label: 'Unknown', className: 'bg-gray-100 text-gray-800' },
  error: { label: 'Error', className: 'bg-gray-100 text-gray-800' },
};

export function StatusBadge({ status }: StatusBadgeProps) {
  const config = statusConfig[status] || statusConfig.unknown;
  
  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${config.className}`}>
      {config.label}
    </span>
  );
}
