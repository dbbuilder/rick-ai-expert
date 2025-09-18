import React from 'react';
import { motion } from 'framer-motion';
import { Bot, Wifi, WifiOff, Key, AlertTriangle } from 'lucide-react';

const Header = ({ connectionStatus, apiKeyStatus, demoMode }) => {
  const getConnectionIcon = () => {
    switch (connectionStatus) {
      case 'connected':
        return <Wifi className="w-5 h-5 text-green-500" />;
      case 'connecting':
        return <Wifi className="w-5 h-5 text-yellow-500 animate-pulse" />;
      default:
        return <WifiOff className="w-5 h-5 text-red-500" />;
    }
  };

  const getConnectionText = () => {
    switch (connectionStatus) {
      case 'connected':
        return 'Connected';
      case 'connecting':
        return 'Connecting...';
      case 'disconnected':
        return 'Disconnected';
      default:
        return 'Connection Error';
    }
  };

  const getAPIStatus = () => {
    if (apiKeyStatus === 'available') {
      return {
        icon: <Key className="w-4 h-4 text-green-500" />,
        text: 'OpenAI Active',
        color: 'text-green-600'
      };
    } else {
      return {
        icon: <AlertTriangle className="w-4 h-4 text-orange-500" />,
        text: 'Demo Mode',
        color: 'text-orange-600'
      };
    }
  };

  const apiStatus = getAPIStatus();

  return (
    <motion.header
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="bg-gradient-to-r from-blue-600 via-blue-700 to-blue-800 text-white shadow-lg"
    >
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          {/* Left: Logo and Title */}
          <div className="flex items-center space-x-4">
            <motion.div
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="w-12 h-12 bg-white rounded-full flex items-center justify-center shadow-lg"
            >
              <Bot className="w-7 h-7 text-blue-600" />
            </motion.div>
            <div>
              <h1 className="text-2xl font-bold">Rick</h1>
              <p className="text-blue-100 text-sm">Anterix Technology Expert</p>
            </div>
          </div>

          {/* Center: Demo Mode Badge */}
          {demoMode && (
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              className="hidden md:flex items-center space-x-2 bg-orange-500 px-4 py-2 rounded-full text-sm font-medium"
            >
              <AlertTriangle className="w-4 h-4" />
              <span>Demo Mode - Limited AI Features</span>
            </motion.div>
          )}

          {/* Right: Status Indicators */}
          <div className="flex items-center space-x-6">
            {/* API Status */}
            <div className="hidden sm:flex items-center space-x-2">
              <div className="text-right">
                <div className="text-xs text-blue-100">AI Engine</div>
                <div className={`text-sm font-medium ${apiStatus.color}`}>
                  <div className="flex items-center space-x-1 text-white">
                    {apiStatus.icon}
                    <span>{apiStatus.text}</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Connection Status */}
            <div className="flex items-center space-x-2">
              <div className="text-right">
                <div className="text-xs text-blue-100">Connection</div>
                <div className="text-sm font-medium">
                  <div className="flex items-center space-x-1">
                    {getConnectionIcon()}
                    <span>{getConnectionText()}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Mobile Demo Mode Badge */}
        {demoMode && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            className="md:hidden mt-3 flex items-center justify-center space-x-2 bg-orange-500 px-3 py-2 rounded-full text-sm font-medium"
          >
            <AlertTriangle className="w-4 h-4" />
            <span>Demo Mode Active</span>
          </motion.div>
        )}
      </div>

      {/* Animated line */}
      <motion.div
        className="h-1 bg-gradient-to-r from-blue-400 to-blue-600"
        initial={{ scaleX: 0 }}
        animate={{ scaleX: 1 }}
        transition={{ duration: 1, delay: 0.3 }}
      />
    </motion.header>
  );
};

export default Header;