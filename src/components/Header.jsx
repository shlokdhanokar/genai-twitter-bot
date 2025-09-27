import React, { useState } from 'react';

const Header = ({ refreshStats, loading }) => {
  const [isRunning, setIsRunning] = useState(false);
  const [botOutput, setBotOutput] = useState('');

  const runBot = async () => {
    setIsRunning(true);
    setBotOutput('Starting bot...');
    
    try {
      const response = await fetch('/api/run-bot', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      const data = await response.json();
      
      if (data.success) {
        setBotOutput('✅ Bot executed successfully!');
        refreshStats();
      } else {
        setBotOutput(`❌ Bot execution failed: ${data.message}`);
      }
    } catch (error) {
      setBotOutput(`❌ Error: ${error.message}`);
    } finally {
      setIsRunning(false);
      // Clear output after 5 seconds
      setTimeout(() => setBotOutput(''), 5000);
    }
  };

  return (
    <header className="bg-white/80 backdrop-blur-sm border-b border-gray-200 px-8 py-6 sticky top-0 z-10">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">
            Twitter News Bot
          </h1>
          <p className="text-gray-600 mt-1">Automated news posting dashboard</p>
        </div>
        
        <div className="flex items-center space-x-4">
          {botOutput && (
            <div className="bg-gray-100 px-4 py-2 rounded-lg text-sm font-mono max-w-md">
              {botOutput}
            </div>
          )}
          
          <button
            onClick={runBot}
            disabled={isRunning}
            className="btn-hover bg-gradient-to-r from-indigo-600 to-purple-600 text-white px-6 py-3 rounded-xl font-semibold shadow-lg disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
          >
            {isRunning ? (
              <>
                <div className="spinner"></div>
                <span>Running...</span>
              </>
            ) : (
              <>
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.828 14.828a4 4 0 01-5.656 0M9 10h1m4 0h1m-6 4h1m4 0h1m-6-8h8a2 2 0 012 2v8a2 2 0 01-2 2H8a2 2 0 01-2-2V8a2 2 0 012-2z" />
                </svg>
                <span>Run Bot</span>
              </>
            )}
          </button>
          
          <button
            onClick={refreshStats}
            disabled={loading}
            className="btn-hover bg-white text-gray-700 px-4 py-3 rounded-xl font-semibold shadow-md border border-gray-200 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? (
              <div className="spinner"></div>
            ) : (
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
            )}
          </button>
        </div>
      </div>
    </header>
  );
};

export default Header;