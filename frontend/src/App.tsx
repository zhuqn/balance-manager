import { useState } from 'react';
import { useBalanceData } from './hooks/useBalanceData';
import { Navbar } from './components/Navbar';
import { SummaryStats } from './components/SummaryStats';
import { PlatformCard } from './components/PlatformCard';
import { ManualEntryModal } from './components/ManualEntryModal';
import type { PlatformBalance } from './types';

function App() {
  const { summary, loading, error, refresh, refreshPlatform } = useBalanceData();
  const [modalOpen, setModalOpen] = useState(false);
  const [selectedPlatform, setSelectedPlatform] = useState<string>('');
  const [refreshing, setRefreshing] = useState(false);

  const handleRefresh = async () => {
    setRefreshing(true);
    try {
      await refresh();
    } finally {
      setRefreshing(false);
    }
  };

  const handleEnterBalance = (platformName: string) => {
    setSelectedPlatform(platformName);
    setModalOpen(true);
  };

  const handleModalSubmit = (balance: PlatformBalance) => {
    console.log('Balance submitted:', balance);
    // The data is already updated via the API call
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading balances...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-600 mb-4">Error: {error}</p>
          <button
            onClick={handleRefresh}
            className="px-4 py-2 bg-primary-500 text-white rounded-md hover:bg-primary-600"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  if (!summary) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gray-100">
      <Navbar onRefresh={handleRefresh} refreshing={refreshing} />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <SummaryStats summary={summary} />

        <div className="mb-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">
            Platform Balances
          </h2>
          <p className="text-gray-600 mb-4">
            Last updated: {new Date(summary.generated_at).toLocaleString()}
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {summary.balances.map((balance) => (
            <PlatformCard
              key={balance.platform}
              balance={balance}
              onRefresh={refreshPlatform}
              onEnterBalance={handleEnterBalance}
            />
          ))}
        </div>

        {summary.balances.length === 0 && (
          <div className="text-center py-12">
            <p className="text-gray-600">No platforms configured</p>
          </div>
        )}
      </main>

      <ManualEntryModal
        platformName={selectedPlatform}
        isOpen={modalOpen}
        onClose={() => setModalOpen(false)}
        onSubmit={handleModalSubmit}
      />
    </div>
  );
}

export default App;
