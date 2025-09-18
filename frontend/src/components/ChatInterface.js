import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Send, Bot, User, Loader2, AlertCircle } from 'lucide-react';
import ReactMarkdown from 'react-markdown';

const ChatInterface = ({
  messages,
  onSendMessage,
  isTyping,
  isConnected,
  error,
  demoMode
}) => {
  const [inputMessage, setInputMessage] = useState('');
  const [isComposing, setIsComposing] = useState(false);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(scrollToBottom, [messages, isTyping]);

  const handleSend = () => {
    if (inputMessage.trim() && isConnected && !isComposing) {
      onSendMessage(inputMessage.trim());
      setInputMessage('');
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const getSuggestions = () => [
    "What is Private LTE?",
    "How does 900 MHz spectrum work?",
    "What's the business case for utilities?",
    "Tell me about grid modernization",
    "How does Anterix ensure security?",
    "What utilities use Anterix solutions?"
  ];

  const formatMessage = (content) => {
    // Enhanced message formatting for better display
    if (typeof content !== 'string') return content;

    return content
      .replace(/\*\*(.*?)\*\*/g, '**$1**') // Keep markdown bold
      .replace(/• /g, '\n• ') // Format bullet points
      .trim();
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
      {/* Chat Header */}
      <div className="bg-gradient-to-r from-blue-600 to-blue-700 text-white p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-white rounded-full flex items-center justify-center">
              <Bot className="w-6 h-6 text-blue-600" />
            </div>
            <div>
              <h2 className="font-bold text-lg">Rick</h2>
              <p className="text-blue-100 text-sm">Anterix Technology Expert</p>
            </div>
          </div>

          {demoMode && (
            <div className="bg-orange-500 px-3 py-1 rounded-full text-xs font-medium">
              Demo Mode
            </div>
          )}
        </div>
      </div>

      {/* Messages Area */}
      <div className="h-96 overflow-y-auto p-4 space-y-4 bg-gray-50">
        {messages.length === 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center py-8"
          >
            <Bot className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-gray-600 font-medium mb-2">
              Welcome to Rick, your Anterix AI Expert!
            </h3>
            <p className="text-gray-500 text-sm mb-4">
              I can help you understand Anterix solutions, Private LTE technology, and grid modernization.
            </p>

            {/* Suggestion Pills */}
            <div className="flex flex-wrap gap-2 justify-center max-w-md mx-auto">
              {getSuggestions().slice(0, 3).map((suggestion, index) => (
                <button
                  key={index}
                  onClick={() => setInputMessage(suggestion)}
                  className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-xs hover:bg-blue-200 transition-colors"
                >
                  {suggestion}
                </button>
              ))}
            </div>
          </motion.div>
        )}

        <AnimatePresence>
          {messages.map((message, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.3 }}
              className={`flex ${message.isUser ? 'justify-end' : 'justify-start'}`}
            >
              <div className={`flex items-start space-x-2 max-w-3xl ${
                message.isUser ? 'flex-row-reverse space-x-reverse' : ''
              }`}>
                {/* Avatar */}
                <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                  message.isUser
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-200 text-gray-600'
                }`}>
                  {message.isUser ? (
                    <User className="w-4 h-4" />
                  ) : (
                    <Bot className="w-4 h-4" />
                  )}
                </div>

                {/* Message Bubble */}
                <div className={`px-4 py-2 rounded-lg ${
                  message.isUser
                    ? 'bg-blue-600 text-white'
                    : 'bg-white border border-gray-200 text-gray-800'
                }`}>
                  <div className="prose prose-sm max-w-none">
                    <ReactMarkdown>{formatMessage(message.content)}</ReactMarkdown>
                  </div>

                  {/* Message metadata */}
                  {message.timestamp && (
                    <div className={`text-xs mt-1 ${
                      message.isUser ? 'text-blue-100' : 'text-gray-500'
                    }`}>
                      {new Date(message.timestamp).toLocaleTimeString()}
                    </div>
                  )}

                  {/* Knowledge sources */}
                  {message.knowledge_sources && message.knowledge_sources.length > 0 && (
                    <div className="mt-2 pt-2 border-t border-gray-100">
                      <div className="text-xs text-gray-500 mb-1">Sources:</div>
                      {message.knowledge_sources.slice(0, 2).map((source, idx) => (
                        <div key={idx} className="text-xs">
                          <a
                            href={source.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-blue-600 hover:underline"
                          >
                            📄 {source.title}
                          </a>
                        </div>
                      ))}
                    </div>
                  )}

                  {/* Suggested actions */}
                  {message.suggested_actions && message.suggested_actions.length > 0 && (
                    <div className="mt-2 flex flex-wrap gap-1">
                      {message.suggested_actions.map((action, idx) => (
                        <button
                          key={idx}
                          className="px-2 py-1 bg-blue-100 text-blue-700 rounded text-xs hover:bg-blue-200 transition-colors"
                        >
                          {action}
                        </button>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            </motion.div>
          ))}
        </AnimatePresence>

        {/* Typing Indicator */}
        {isTyping && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex justify-start"
          >
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center">
                <Bot className="w-4 h-4 text-gray-600" />
              </div>
              <div className="bg-white border border-gray-200 px-4 py-2 rounded-lg">
                <div className="flex items-center space-x-1">
                  <Loader2 className="w-4 h-4 animate-spin text-gray-500" />
                  <span className="text-gray-500 text-sm">Rick is thinking...</span>
                </div>
              </div>
            </div>
          </motion.div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Connection Error */}
      {!isConnected && (
        <div className="bg-red-50 border-t border-red-200 p-3">
          <div className="flex items-center space-x-2 text-red-700">
            <AlertCircle className="w-4 h-4" />
            <span className="text-sm">
              Connection lost. Attempting to reconnect...
            </span>
          </div>
        </div>
      )}

      {/* Input Area */}
      <div className="border-t border-gray-200 p-4">
        <div className="flex space-x-3">
          <div className="flex-1">
            <textarea
              ref={inputRef}
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              onCompositionStart={() => setIsComposing(true)}
              onCompositionEnd={() => setIsComposing(false)}
              placeholder={
                isConnected
                  ? "Ask Rick about Anterix solutions, Private LTE, grid modernization..."
                  : "Connecting to Rick..."
              }
              disabled={!isConnected}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
              rows="2"
            />
          </div>
          <button
            onClick={handleSend}
            disabled={!inputMessage.trim() || !isConnected || isComposing}
            className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed text-white px-6 py-3 rounded-lg font-medium transition-colors duration-200 flex items-center space-x-2"
          >
            <Send className="w-4 h-4" />
            <span>Send</span>
          </button>
        </div>

        {/* Quick suggestions when empty */}
        {inputMessage === '' && messages.length > 0 && (
          <div className="mt-3">
            <div className="text-xs text-gray-500 mb-2">Try asking:</div>
            <div className="flex flex-wrap gap-2">
              {getSuggestions().slice(3, 6).map((suggestion, index) => (
                <button
                  key={index}
                  onClick={() => setInputMessage(suggestion)}
                  className="px-3 py-1 bg-gray-100 text-gray-700 rounded-full text-xs hover:bg-gray-200 transition-colors"
                >
                  {suggestion}
                </button>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ChatInterface;