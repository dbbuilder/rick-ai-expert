import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Settings, Key, HelpCircle, ExternalLink, AlertTriangle } from 'lucide-react';

const DemoControls = ({ onToggleDemo, apiKeyStatus }) => {
  const [showApiKeyInfo, setShowApiKeyInfo] = useState(false);

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ delay: 0.1 }}
      className="bg-gradient-to-br from-orange-50 to-orange-100 border-2 border-orange-200 rounded-lg p-4"
    >
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center space-x-2">
          <Settings className="w-5 h-5 text-orange-600" />
          <h3 className="font-semibold text-orange-800">Demo Mode</h3>
        </div>
        <button
          onClick={() => setShowApiKeyInfo(!showApiKeyInfo)}
          className="text-orange-600 hover:text-orange-800 transition-colors"
        >
          <HelpCircle className="w-4 h-4" />
        </button>
      </div>

      <div className="space-y-3">
        <div className="flex items-start space-x-2 text-sm">
          <AlertTriangle className="w-4 h-4 text-orange-500 mt-0.5 flex-shrink-0" />
          <div className="text-orange-700">
            <p className="font-medium mb-1">Limited AI Features Active</p>
            <p className="text-xs">
              Rick is using pre-programmed responses. For full AI capabilities, configure OpenAI API.
            </p>
          </div>
        </div>

        <AnimatePresence>
          {showApiKeyInfo && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="bg-white border border-orange-200 rounded-lg p-3 text-sm"
            >
              <div className="space-y-3">
                <div>
                  <h4 className="font-medium text-gray-800 mb-2 flex items-center">
                    <Key className="w-4 h-4 mr-1" />
                    Enable Full AI Features
                  </h4>
                  <p className="text-gray-600 text-xs mb-2">
                    To unlock Rick's full potential, you need an OpenAI API key:
                  </p>
                </div>

                <div className="space-y-2 text-xs">
                  <div className="bg-gray-50 p-2 rounded border">
                    <p className="font-medium text-gray-700 mb-1">1. Get API Key:</p>
                    <a
                      href="https://platform.openai.com/api-keys"
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-blue-600 hover:underline flex items-center"
                    >
                      OpenAI Platform <ExternalLink className="w-3 h-3 ml-1" />
                    </a>
                  </div>

                  <div className="bg-gray-50 p-2 rounded border">
                    <p className="font-medium text-gray-700 mb-1">2. Set Environment Variable:</p>
                    <code className="bg-gray-200 px-1 rounded text-xs">
                      OPENAI_API_KEY=your-key-here
                    </code>
                  </div>

                  <div className="bg-gray-50 p-2 rounded border">
                    <p className="font-medium text-gray-700 mb-1">3. Restart Rick:</p>
                    <code className="bg-gray-200 px-1 rounded text-xs">
                      python rick.py
                    </code>
                  </div>
                </div>

                <div className="border-t border-gray-200 pt-2">
                  <p className="text-xs text-gray-500">
                    💡 <strong>Cost:</strong> ~$0.004 per conversation (~$4 for 1,000 conversations)
                  </p>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Demo Features List */}
        <div className="bg-white border border-orange-200 rounded-lg p-3">
          <h4 className="font-medium text-gray-800 mb-2 text-sm">Current Demo Features:</h4>
          <ul className="space-y-1 text-xs text-gray-600">
            <li className="flex items-center">
              <span className="w-1.5 h-1.5 bg-green-400 rounded-full mr-2"></span>
              Knowledge base search
            </li>
            <li className="flex items-center">
              <span className="w-1.5 h-1.5 bg-green-400 rounded-full mr-2"></span>
              Pre-programmed responses
            </li>
            <li className="flex items-center">
              <span className="w-1.5 h-1.5 bg-green-400 rounded-full mr-2"></span>
              Basic Anterix information
            </li>
            <li className="flex items-center">
              <span className="w-1.5 h-1.5 bg-red-400 rounded-full mr-2"></span>
              Dynamic conversation flow
            </li>
            <li className="flex items-center">
              <span className="w-1.5 h-1.5 bg-red-400 rounded-full mr-2"></span>
              Complex technical questions
            </li>
            <li className="flex items-center">
              <span className="w-1.5 h-1.5 bg-red-400 rounded-full mr-2"></span>
              Personalized recommendations
            </li>
          </ul>
        </div>

        {/* Quick Demo Actions */}
        <div className="bg-white border border-orange-200 rounded-lg p-3">
          <h4 className="font-medium text-gray-800 mb-2 text-sm">Try Demo Questions:</h4>
          <div className="grid grid-cols-1 gap-1">
            {[
              "What is Private LTE?",
              "Tell me about 900 MHz",
              "Grid modernization benefits",
              "Anterix business case"
            ].map((question, index) => (
              <button
                key={index}
                onClick={() => {
                  // This would trigger sending the message
                  const event = new CustomEvent('send-demo-message', {
                    detail: { message: question }
                  });
                  window.dispatchEvent(event);
                }}
                className="text-left px-2 py-1 text-xs text-orange-700 hover:bg-orange-50 rounded transition-colors"
              >
                💬 {question}
              </button>
            ))}
          </div>
        </div>
      </div>
    </motion.div>
  );
};

export default DemoControls;