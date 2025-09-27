import React, { useState, useEffect } from 'react';

const Logs = ({ refreshStats }) => {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');

  useEffect(() => {
    fetchLogs();
  }, []);

  const fetchLogs = async () => {
    try {
      const response = await fetch('/api/logs');
      const data = await response.json();
      setLogs(data);
    } catch (error) {
      console.error('Error fetching logs:', error);
    } finally {
      setLoading(false);
    }
  };

  const clearLogs = async () => {
    if (window.confirm('Are you sure you want to clear all logs?')) {
      try {
        await fetch('/api/logs', { method: 'DELETE' });
        setLogs([]);
        refreshStats();
      } catch (error) {
        console.error('Error clearing logs:', error);
      }
    }
  };

  const filteredLogs = logs.filter(log => {
    if (filter === 'success') return log.success;
    if (filter === 'failed') return !log.success;
    return true;
  });

  const formatDate = (timestamp) => {
    return new Date(timestamp).toLocaleString();
  };

  const truncateText = (text, maxLength = 100) => {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="spinner"></div>
        <span className="ml-3 text-gray-600">Loading logs...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Tweet Logs</h2>
          <p className="text-gray-600">View and manage your bot's tweet history</p>
        </div>
        
        <div className="flex items-center space-x-4">
          <select
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
          >
            <option value="all">All Tweets</option>
            <option value="success">Successful</option>
            <option value="failed">Failed</option>
          </select>
          
          <button
            onClick={fetchLogs}
            className="btn-hover bg-indigo-100 text-indigo-700 px-4 py-2 rounded-lg font-medium hover:bg-indigo-200 flex items-center space-x-2"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            <span>Refresh</span>
          </button>
          
          <button
            onClick={clearLogs}
            className="btn-hover bg-red-100 text-red-700 px-4 py-2 rounded-lg font-medium hover:bg-red-200 flex items-center space-x-2"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
            <span>Clear Logs</span>
          </button>
        </div>
      </div>

      {filteredLogs.length === 0 ? (
        <div className="bg-white rounded-2xl p-12 shadow-lg border border-gray-100 text-center">
          <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">No logs found</h3>
          <p className="text-gray-600">Run the bot to see tweet logs appear here</p>
        </div>
      ) : (
        <div className="space-y-4">
          {filteredLogs.map((log, index) => (
            <div
              key={index}
              className="bg-white rounded-xl p-6 shadow-md border border-gray-100 hover:shadow-lg transition-shadow duration-200"
            >
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center space-x-3">
                  <div className={`w-3 h-3 rounded-full ${log.success ? 'bg-green-500' : 'bg-red-500'}`}></div>
                  <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
                    log.success 
                      ? 'bg-green-100 text-green-800' 
                      : 'bg-red-100 text-red-800'
                  }`}>
                    {log.success ? 'Success' : 'Failed'}
                  </span>
                </div>
                <span className="text-sm text-gray-500">{formatDate(log.timestamp)}</span>
              </div>
              
              <h4 className="font-semibold text-gray-900 mb-2">{log.title}</h4>
              
              <div className="bg-gray-50 rounded-lg p-4 mb-3">
                <p className="text-sm text-gray-700 font-mono">{truncateText(log.tweet)}</p>
              </div>
              
              {log.link && (
                <a
                  href={log.link}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center space-x-2 text-indigo-600 hover:text-indigo-800 text-sm font-medium"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                  </svg>
                  <span>View Source</span>
                </a>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default Logs;