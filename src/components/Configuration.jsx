import React, { useState, useEffect } from 'react';

const Configuration = ({ refreshStats }) => {
  const [config, setConfig] = useState({});
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState('');

  useEffect(() => {
    fetchConfig();
  }, []);

  const fetchConfig = async () => {
    try {
      const response = await fetch('/api/config');
      const data = await response.json();
      setConfig(data);
    } catch (error) {
      console.error('Error fetching config:', error);
      setMessage('Error loading configuration');
    } finally {
      setLoading(false);
    }
  };

  const saveConfig = async () => {
    setSaving(true);
    try {
      const response = await fetch('/api/config', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(config),
      });

      if (response.ok) {
        setMessage('✅ Configuration saved successfully!');
        refreshStats();
      } else {
        setMessage('❌ Failed to save configuration');
      }
    } catch (error) {
      setMessage('❌ Error saving configuration');
    } finally {
      setSaving(false);
      setTimeout(() => setMessage(''), 3000);
    }
  };

  const updateConfig = (path, value) => {
    setConfig(prev => {
      const newConfig = { ...prev };
      const keys = path.split('.');
      let current = newConfig;
      
      for (let i = 0; i < keys.length - 1; i++) {
        if (!current[keys[i]]) current[keys[i]] = {};
        current = current[keys[i]];
      }
      
      current[keys[keys.length - 1]] = value;
      return newConfig;
    });
  };

  const addKeyword = () => {
    const keywords = config.priority_keywords || [];
    keywords.push('');
    updateConfig('priority_keywords', keywords);
  };

  const removeKeyword = (index) => {
    const keywords = [...(config.priority_keywords || [])];
    keywords.splice(index, 1);
    updateConfig('priority_keywords', keywords);
  };

  const updateKeyword = (index, value) => {
    const keywords = [...(config.priority_keywords || [])];
    keywords[index] = value;
    updateConfig('priority_keywords', keywords);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="spinner"></div>
        <span className="ml-3 text-gray-600">Loading configuration...</span>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Bot Configuration</h2>
          <p className="text-gray-600">Customize your Twitter news bot settings</p>
        </div>
        
        <button
          onClick={saveConfig}
          disabled={saving}
          className="btn-hover bg-gradient-to-r from-indigo-600 to-purple-600 text-white px-6 py-3 rounded-xl font-semibold shadow-lg disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
        >
          {saving ? (
            <>
              <div className="spinner"></div>
              <span>Saving...</span>
            </>
          ) : (
            <>
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-3m-1 4l-3 3m0 0l-3-3m3 3V4" />
              </svg>
              <span>Save Configuration</span>
            </>
          )}
        </button>
      </div>

      {message && (
        <div className={`p-4 rounded-xl ${message.includes('✅') ? 'bg-green-50 text-green-800 border border-green-200' : 'bg-red-50 text-red-800 border border-red-200'}`}>
          {message}
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Basic Settings */}
        <div className="bg-white rounded-2xl p-6 shadow-lg border border-gray-100">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Basic Settings</h3>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Tweets per Run
              </label>
              <input
                type="number"
                min="1"
                max="10"
                value={config.tweets_per_run || 3}
                onChange={(e) => updateConfig('tweets_per_run', parseInt(e.target.value))}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Max News Age (days)
              </label>
              <input
                type="number"
                min="1"
                max="7"
                value={config.max_news_age || 2}
                onChange={(e) => updateConfig('max_news_age', parseInt(e.target.value))}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Tweet Delay (seconds)
              </label>
              <input
                type="number"
                min="10"
                max="3600"
                value={config.tweet_delay || 300}
                onChange={(e) => updateConfig('tweet_delay', parseInt(e.target.value))}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Tweet Method
              </label>
              <select
                value={config.tweet_method || 'selenium'}
                onChange={(e) => updateConfig('tweet_method', e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              >
                <option value="selenium">Selenium (Browser Automation)</option>
                <option value="api">Twitter API</option>
              </select>
            </div>
          </div>
        </div>

        {/* Category Weights */}
        <div className="bg-white rounded-2xl p-6 shadow-lg border border-gray-100">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Category Weights</h3>
          
          <div className="space-y-4">
            {Object.entries(config.category_weights || {}).map(([category, weight]) => (
              <div key={category} className="flex items-center space-x-3">
                <label className="flex-1 text-sm font-medium text-gray-700 capitalize">
                  {category}
                </label>
                <input
                  type="range"
                  min="1"
                  max="10"
                  value={weight}
                  onChange={(e) => updateConfig(`category_weights.${category}`, parseInt(e.target.value))}
                  className="flex-1"
                />
                <span className="w-8 text-sm font-semibold text-gray-900">{weight}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Priority Keywords */}
      <div className="bg-white rounded-2xl p-6 shadow-lg border border-gray-100">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">Priority Keywords</h3>
          <button
            onClick={addKeyword}
            className="btn-hover bg-indigo-100 text-indigo-700 px-4 py-2 rounded-lg font-medium hover:bg-indigo-200 flex items-center space-x-2"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
            </svg>
            <span>Add Keyword</span>
          </button>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
          {(config.priority_keywords || []).map((keyword, index) => (
            <div key={index} className="flex items-center space-x-2">
              <input
                type="text"
                value={keyword}
                onChange={(e) => updateKeyword(index, e.target.value)}
                placeholder="Enter keyword"
                className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent text-sm"
              />
              <button
                onClick={() => removeKeyword(index)}
                className="text-red-500 hover:text-red-700 p-1"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
              </button>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Configuration;