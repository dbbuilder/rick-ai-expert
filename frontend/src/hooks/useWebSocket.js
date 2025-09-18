import { useState, useEffect, useRef, useCallback } from 'react';

export const useWebSocket = ({ onConnectionChange }) => {
  const [messages, setMessages] = useState([]);
  const [isTyping, setIsTyping] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState('connecting');
  const [error, setError] = useState(null);

  const wsRef = useRef(null);
  const clientIdRef = useRef(null);
  const reconnectTimeoutRef = useRef(null);
  const reconnectAttemptsRef = useRef(0);

  // Generate unique client ID
  const generateClientId = useCallback(() => {
    return 'client_' + Math.random().toString(36).substr(2, 9) + '_' + Date.now();
  }, []);

  // Connect to WebSocket
  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      return;
    }

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = process.env.NODE_ENV === 'development'
      ? 'localhost:8080'
      : window.location.host;

    if (!clientIdRef.current) {
      clientIdRef.current = generateClientId();
    }

    const wsUrl = `${protocol}//${host}/ws/${clientIdRef.current}`;

    console.log('Connecting to:', wsUrl);
    setConnectionStatus('connecting');

    try {
      wsRef.current = new WebSocket(wsUrl);

      wsRef.current.onopen = () => {
        console.log('WebSocket connected');
        setConnectionStatus('connected');
        setError(null);
        reconnectAttemptsRef.current = 0;

        if (onConnectionChange) {
          onConnectionChange(true);
        }
      };

      wsRef.current.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          handleMessage(message);
        } catch (err) {
          console.error('Failed to parse message:', err);
        }
      };

      wsRef.current.onclose = (event) => {
        console.log('WebSocket closed:', event.code, event.reason);
        setConnectionStatus('disconnected');
        setIsTyping(false);

        if (onConnectionChange) {
          onConnectionChange(false);
        }

        // Attempt to reconnect if not a deliberate close
        if (event.code !== 1000 && reconnectAttemptsRef.current < 5) {
          const delay = Math.min(1000 * Math.pow(2, reconnectAttemptsRef.current), 30000);
          console.log(`Reconnecting in ${delay}ms (attempt ${reconnectAttemptsRef.current + 1})`);

          reconnectTimeoutRef.current = setTimeout(() => {
            reconnectAttemptsRef.current += 1;
            connect();
          }, delay);
        } else {
          setError('Connection failed. Please refresh the page.');
        }
      };

      wsRef.current.onerror = (error) => {
        console.error('WebSocket error:', error);
        setError('Connection error occurred');
        setConnectionStatus('error');
      };

    } catch (err) {
      console.error('Failed to create WebSocket:', err);
      setError('Failed to establish connection');
      setConnectionStatus('error');
    }
  }, [generateClientId, onConnectionChange]);

  // Handle incoming messages
  const handleMessage = useCallback((message) => {
    console.log('Received message:', message);

    switch (message.type) {
      case 'message':
        setMessages(prev => [...prev, {
          content: message.content,
          isUser: false,
          timestamp: message.timestamp,
          speaker: message.speaker,
          suggested_actions: message.suggested_actions,
          knowledge_sources: message.knowledge_sources
        }]);
        setIsTyping(false);
        break;

      case 'typing':
        setIsTyping(true);
        break;

      case 'feedback_ack':
        // Handle feedback acknowledgment
        console.log('Feedback acknowledged:', message.content);
        break;

      default:
        console.log('Unknown message type:', message.type);
    }
  }, []);

  // Send message
  const sendMessage = useCallback((content) => {
    if (wsRef.current?.readyState !== WebSocket.OPEN) {
      setError('Not connected to chat service');
      return;
    }

    if (!content.trim()) {
      return;
    }

    // Add user message to UI immediately
    const userMessage = {
      content: content,
      isUser: true,
      timestamp: new Date().toISOString(),
      speaker: 'You'
    };

    setMessages(prev => [...prev, userMessage]);

    // Send to server
    try {
      wsRef.current.send(JSON.stringify({
        type: 'chat',
        message: content
      }));
    } catch (err) {
      console.error('Failed to send message:', err);
      setError('Failed to send message');
    }
  }, []);

  // Send feedback
  const sendFeedback = useCallback((feedback) => {
    if (wsRef.current?.readyState !== WebSocket.OPEN) {
      return;
    }

    try {
      wsRef.current.send(JSON.stringify({
        type: 'feedback',
        feedback: feedback
      }));
    } catch (err) {
      console.error('Failed to send feedback:', err);
    }
  }, []);

  // Clear error
  const clearError = useCallback(() => {
    setError(null);
  }, []);

  // Clear messages
  const clearMessages = useCallback(() => {
    setMessages([]);
  }, []);

  // Connect on mount
  useEffect(() => {
    connect();

    // Cleanup on unmount
    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }

      if (wsRef.current) {
        wsRef.current.close(1000, 'Component unmounting');
      }
    };
  }, [connect]);

  // Auto-clear errors after 5 seconds
  useEffect(() => {
    if (error) {
      const timeout = setTimeout(() => {
        setError(null);
      }, 5000);

      return () => clearTimeout(timeout);
    }
  }, [error]);

  return {
    messages,
    isTyping,
    connectionStatus,
    error,
    sendMessage,
    sendFeedback,
    clearError,
    clearMessages,
    reconnect: connect
  };
};