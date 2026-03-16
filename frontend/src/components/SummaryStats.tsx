import type { SystemSummary } from '../types';

interface SummaryStatsProps {
  summary: SystemSummary;
}

export function SummaryStats({ summary }: SummaryStatsProps) {
  const stats = [
    {
      label: 'Total Platforms',
      value: summary.platform_count,
      className: 'bg-blue-50 text-blue-700',
    },
    {
      label: 'Active',
      value: summary.platforms_active,
      className: 'bg-green-50 text-green-700',
    },
    {
      label: 'Warning',
      value: summary.platforms_warning,
      className: 'bg-yellow-50 text-yellow-700',
    },
    {
      label: 'Critical',
      value: summary.platforms_critical,
      className: 'bg-red-50 text-red-700',
    },
    {
      label: 'Error',
      value: summary.platforms_error,
      className: 'bg-gray-50 text-gray-700',
    },
  ];

  return (
    <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-8">
      {stats.map((stat) => (
        <div
          key={stat.label}
          className={`${stat.className} rounded-lg p-4 text-center`}
        >
          <p className="text-2xl font-bold">{stat.value}</p>
          <p className="text-sm opacity-80">{stat.label}</p>
        </div>
      ))}
    </div>
  );
}
