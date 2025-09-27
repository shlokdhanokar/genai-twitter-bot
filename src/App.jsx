import React, { useState, useEffect } from 'react';
import Dashboard from './components/Dashboard';
import Configuration from './components/Configuration';
import Logs from './components/Logs';
import Header from './components/Header';
import Sidebar from './components/Sidebar';

function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [stats, setStats] = useState({});
  const [loading, setLoading] = useState(true);

  const fetchStats = async () => {
    try {
      const response = await fetch('/api/stats');
      const data = await response.json();
      setStats(data);
    } catch (error) {
      console.error('Error fetching stats:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStats();
    // Refresh stats every 30 seconds
    const interval = setInterval(fetchStats, 30000);
    return () => clearInterval(interval);
  }, []);

  const refreshStats = () => {
    setLoading(true);
    fetchStats();
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50">
      <div className="flex">
        <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} stats={stats} />
        
        <div className="flex-1 ml-64">
          <Header refreshStats={refreshStats} loading={loading} />
          
          <main className="p-8">
            <div className="animate-fadeIn">
              {activeTab === 'dashboard' && (
                <Dashboard stats={stats} refreshStats={refreshStats} />
              )}
              {activeTab === 'configuration' && (
                <Configuration refreshStats={refreshStats} />
              )}
              {activeTab === 'logs' && (
                <Logs refreshStats={refreshStats} />
              )}
            </div>
          </main>
        </div>
      </div>
    </div>
  );
}

export default App;