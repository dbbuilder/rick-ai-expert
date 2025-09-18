import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import ChatInterface from './components/ChatInterface';
import Header from './components/Header';
import KnowledgeBaseStats from './components/KnowledgeBaseStats';
import DemoControls from './components/DemoControls';
import { useWebSocket } from './hooks/useWebSocket';
import './App.css';

function App() {
  const [isConnected, setIsConnected] = useState(false);
  const [knowledgeStats, setKnowledgeStats] = useState(null);
  const [demoMode, setDemoMode] = useState(false);
  const [apiKeyStatus, setApiKeyStatus] = useState('unknown');

  const {
    messages,
    sendMessage,
    isTyping,
    connectionStatus,
    error
  } = useWebSocket({
    onConnectionChange: setIsConnected
  });

  // Check system status on mount
  useEffect(() => {
    checkSystemStatus();
  }, []);

  const checkSystemStatus = async () => {
    try {
      const response = await fetch('/health');
      const data = await response.json();

      setKnowledgeStats(data.knowledge_base);
      setApiKeyStatus(data.ai_engine?.has_api_key ? 'available' : 'missing');
      setDemoMode(!data.ai_engine?.has_api_key);
    } catch (error) {
      console.error('Failed to check system status:', error);
      setDemoMode(true);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-blue-50">
      <Header
        connectionStatus={connectionStatus}
        apiKeyStatus={apiKeyStatus}
        demoMode={demoMode}
      />

      <main className="container mx-auto px-4 py-6 max-w-7xl">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="grid grid-cols-1 lg:grid-cols-4 gap-6"
        >
          {/* Main Chat Interface */}
          <div className="lg:col-span-3">
            <ChatInterface
              messages={messages}
              onSendMessage={sendMessage}
              isTyping={isTyping}
              isConnected={isConnected}
              error={error}
              demoMode={demoMode}
            />
          </div>

          {/* Sidebar */}
          <div className="lg:col-span-1 space-y-6">
            {/* Demo Controls */}
            {demoMode && (
              <DemoControls
                onToggleDemo={setDemoMode}
                apiKeyStatus={apiKeyStatus}
              />
            )}

            {/* Knowledge Base Stats */}
            <KnowledgeBaseStats stats={knowledgeStats} />

            {/* System Status */}
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.2 }}
              className="bg-white rounded-lg shadow-sm border border-gray-200 p-4"
            >
              <h3 className="font-semibold text-gray-800 mb-3 flex items-center">
                <div className="w-2 h-2 bg-green-400 rounded-full mr-2"></div>
                System Status
              </h3>

              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600">Connection:</span>
                  <span className={`font-medium ${
                    connectionStatus === 'connected' ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {connectionStatus}
                  </span>
                </div>

                <div className="flex justify-between">
                  <span className="text-gray-600">AI Engine:</span>
                  <span className={`font-medium ${
                    apiKeyStatus === 'available' ? 'text-green-600' : 'text-orange-600'
                  }`}>
                    {apiKeyStatus === 'available' ? 'OpenAI Active' : 'Demo Mode'}
                  </span>
                </div>

                <div className="flex justify-between">
                  <span className="text-gray-600">Knowledge Base:</span>
                  <span className="font-medium text-blue-600">
                    {knowledgeStats?.total_items || 0} items
                  </span>
                </div>
              </div>
            </motion.div>

            {/* Quick Actions */}
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.3 }}
              className="bg-white rounded-lg shadow-sm border border-gray-200 p-4"
            >
              <h3 className="font-semibold text-gray-800 mb-3">Quick Actions</h3>
              <div className="space-y-2">
                <button
                  onClick={() => sendMessage("What is Private LTE?")}
                  className="w-full text-left p-2 text-sm text-blue-700 bg-blue-50 rounded hover:bg-blue-100 transition-colors"
                >
                  💡 Ask about Private LTE
                </button>
                <button
                  onClick={() => sendMessage("How can Anterix help my utility?")}
                  className="w-full text-left p-2 text-sm text-blue-700 bg-blue-50 rounded hover:bg-blue-100 transition-colors"
                >
                  🏢 Utility Solutions
                </button>
                <button
                  onClick={() => sendMessage("What's the ROI for Private LTE?")}
                  className="w-full text-left p-2 text-sm text-blue-700 bg-blue-50 rounded hover:bg-blue-100 transition-colors"
                >
                  📊 Business Case
                </button>
                <button
                  onClick={checkSystemStatus}
                  className="w-full text-left p-2 text-sm text-gray-700 bg-gray-50 rounded hover:bg-gray-100 transition-colors"
                >
                  🔄 Refresh Status
                </button>
              </div>
            </motion.div>
          </div>
        </motion.div>
      </main>

      {/* Error Toast */}
      <AnimatePresence>
        {error && (
          <motion.div
            initial={{ opacity: 0, y: 50 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 50 }}
            className="fixed bottom-4 right-4 bg-red-500 text-white p-4 rounded-lg shadow-lg z-50"
          >
            <div className="flex items-center space-x-2">
              <span>⚠️</span>
              <span>{error}</span>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

export default App;