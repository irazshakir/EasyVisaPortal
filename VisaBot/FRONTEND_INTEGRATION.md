# VisaBot Frontend Integration Guide

This guide explains how to integrate the VisaBot API with your React frontend application.

## API Endpoints

### REST API Endpoints

#### 1. Chat Endpoints

**POST** `/api/v1/chat/`
- Send a message to the bot
- **Request Body:**
  ```json
  {
    "session_id": "optional-session-id",
    "message": "Hello, I need help with visa application",
    "context": {
      "user_id": "optional-user-id",
      "language": "en"
    }
  }
  ```
- **Response:**
  ```json
  {
    "session_id": "generated-session-id",
    "message": "Hello! I'm here to help you with your visa application...",
    "state": "greeting",
    "metadata": {
      "intent": "greeting",
      "confidence": 0.95
    },
    "timestamp": "2024-01-15T10:30:00Z"
  }
  ```

**GET** `/api/v1/chat/history/{session_id}`
- Get chat history for a session
- **Response:**
  ```json
  {
    "session_id": "session-id",
    "history": [
      {
        "role": "user",
        "content": "Hello",
        "timestamp": "2024-01-15T10:30:00Z"
      },
      {
        "role": "assistant",
        "content": "Hello! How can I help you?",
        "timestamp": "2024-01-15T10:30:05Z"
      }
    ]
  }
  ```

**DELETE** `/api/v1/chat/session/{session_id}`
- End a chat session

#### 2. WebSocket Endpoints

**WebSocket** `/api/v1/websocket/ws/{session_id}`
- Real-time chat connection
- **Connection:** `ws://localhost:8000/api/v1/websocket/ws/{session_id}`

**GET** `/api/v1/websocket/status/{session_id}`
- Check WebSocket connection status

## Frontend Integration Examples

### 1. REST API Integration (React Hook)

```typescript
// hooks/useVisaBot.ts
import { useState, useCallback } from 'react';

interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

interface ChatResponse {
  session_id: string;
  message: string;
  state: string;
  metadata?: any;
  timestamp: string;
}

export const useVisaBot = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const sendMessage = useCallback(async (message: string) => {
    setIsLoading(true);
    
    try {
      // Add user message to chat
      const userMessage: ChatMessage = {
        role: 'user',
        content: message,
        timestamp: new Date().toISOString()
      };
      setMessages(prev => [...prev, userMessage]);

      // Send to API
      const response = await fetch('/api/v1/chat/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          session_id: sessionId,
          message,
          context: {
            language: 'en'
          }
        })
      });

      const data: ChatResponse = await response.json();
      
      // Set session ID if not already set
      if (!sessionId) {
        setSessionId(data.session_id);
      }

      // Add bot response to chat
      const botMessage: ChatMessage = {
        role: 'assistant',
        content: data.message,
        timestamp: data.timestamp
      };
      setMessages(prev => [...prev, botMessage]);

    } catch (error) {
      console.error('Error sending message:', error);
      // Add error message
      const errorMessage: ChatMessage = {
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date().toISOString()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  }, [sessionId]);

  const loadChatHistory = useCallback(async (sessionId: string) => {
    try {
      const response = await fetch(`/api/v1/chat/history/${sessionId}`);
      const data = await response.json();
      setMessages(data.history);
      setSessionId(sessionId);
    } catch (error) {
      console.error('Error loading chat history:', error);
    }
  }, []);

  const endSession = useCallback(async () => {
    if (sessionId) {
      try {
        await fetch(`/api/v1/chat/session/${sessionId}`, {
          method: 'DELETE'
        });
        setMessages([]);
        setSessionId(null);
      } catch (error) {
        console.error('Error ending session:', error);
      }
    }
  }, [sessionId]);

  return {
    messages,
    sessionId,
    isLoading,
    sendMessage,
    loadChatHistory,
    endSession
  };
};
```

### 2. WebSocket Integration (React Hook)

```typescript
// hooks/useVisaBotWebSocket.ts
import { useState, useEffect, useCallback, useRef } from 'react';

interface WebSocketMessage {
  type: 'connection' | 'message' | 'typing' | 'system' | 'error' | 'pong';
  session_id: string;
  message?: string;
  state?: string;
  metadata?: any;
  timestamp?: string;
  is_typing?: boolean;
  message_type?: string;
}

export const useVisaBotWebSocket = (sessionId: string | null) => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);

  const connect = useCallback(() => {
    if (!sessionId) return;

    const ws = new WebSocket(`ws://localhost:8000/api/v1/websocket/ws/${sessionId}`);
    wsRef.current = ws;

    ws.onopen = () => {
      setIsConnected(true);
      console.log('WebSocket connected');
    };

    ws.onmessage = (event) => {
      const data: WebSocketMessage = JSON.parse(event.data);
      
      switch (data.type) {
        case 'connection':
          // Handle connection message
          break;
        case 'message':
          if (data.message) {
            const botMessage: ChatMessage = {
              role: 'assistant',
              content: data.message,
              timestamp: data.timestamp || new Date().toISOString()
            };
            setMessages(prev => [...prev, botMessage]);
          }
          break;
        case 'typing':
          setIsTyping(data.is_typing || false);
          break;
        case 'system':
          // Handle system messages
          break;
        case 'error':
          console.error('WebSocket error:', data.message);
          break;
      }
    };

    ws.onclose = () => {
      setIsConnected(false);
      console.log('WebSocket disconnected');
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      setIsConnected(false);
    };
  }, [sessionId]);

  const sendMessage = useCallback((message: string) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      // Add user message to chat
      const userMessage: ChatMessage = {
        role: 'user',
        content: message,
        timestamp: new Date().toISOString()
      };
      setMessages(prev => [...prev, userMessage]);

      // Send via WebSocket
      wsRef.current.send(JSON.stringify({
        type: 'message',
        message,
        context: {
          language: 'en'
        }
      }));
    }
  }, []);

  const sendTypingIndicator = useCallback((isTyping: boolean) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        type: 'typing',
        is_typing: isTyping
      }));
    }
  }, []);

  const ping = useCallback(() => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        type: 'ping'
      }));
    }
  }, []);

  useEffect(() => {
    if (sessionId) {
      connect();
    }

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [sessionId, connect]);

  // Keep connection alive with periodic pings
  useEffect(() => {
    if (isConnected) {
      const interval = setInterval(ping, 30000); // Ping every 30 seconds
      return () => clearInterval(interval);
    }
  }, [isConnected, ping]);

  return {
    messages,
    isConnected,
    isTyping,
    sendMessage,
    sendTypingIndicator
  };
};
```

### 3. Chat Component Example

```tsx
// components/VisaBotChat.tsx
import React, { useState } from 'react';
import { useVisaBot } from '../hooks/useVisaBot';

export const VisaBotChat: React.FC = () => {
  const [inputMessage, setInputMessage] = useState('');
  const { messages, isLoading, sendMessage } = useVisaBot();

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (inputMessage.trim() && !isLoading) {
      await sendMessage(inputMessage.trim());
      setInputMessage('');
    }
  };

  return (
    <div className="chat-container">
      <div className="chat-messages">
        {messages.map((message, index) => (
          <div
            key={index}
            className={`message ${message.role === 'user' ? 'user' : 'bot'}`}
          >
            <div className="message-content">{message.content}</div>
            <div className="message-timestamp">
              {new Date(message.timestamp).toLocaleTimeString()}
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="message bot">
            <div className="typing-indicator">Bot is typing...</div>
          </div>
        )}
      </div>
      
      <form onSubmit={handleSendMessage} className="chat-input-form">
        <input
          type="text"
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          placeholder="Type your message..."
          disabled={isLoading}
          className="chat-input"
        />
        <button type="submit" disabled={isLoading || !inputMessage.trim()}>
          Send
        </button>
      </form>
    </div>
  );
};
```

### 4. CSS Styling Example

```css
/* styles/VisaBotChat.css */
.chat-container {
  max-width: 600px;
  margin: 0 auto;
  border: 1px solid #ddd;
  border-radius: 8px;
  overflow: hidden;
}

.chat-messages {
  height: 400px;
  overflow-y: auto;
  padding: 20px;
  background-color: #f9f9f9;
}

.message {
  margin-bottom: 15px;
  display: flex;
  flex-direction: column;
}

.message.user {
  align-items: flex-end;
}

.message.bot {
  align-items: flex-start;
}

.message-content {
  max-width: 70%;
  padding: 10px 15px;
  border-radius: 18px;
  word-wrap: break-word;
}

.message.user .message-content {
  background-color: #007bff;
  color: white;
}

.message.bot .message-content {
  background-color: white;
  border: 1px solid #ddd;
}

.message-timestamp {
  font-size: 12px;
  color: #666;
  margin-top: 5px;
}

.typing-indicator {
  background-color: white;
  border: 1px solid #ddd;
  padding: 10px 15px;
  border-radius: 18px;
  color: #666;
}

.chat-input-form {
  display: flex;
  padding: 15px;
  background-color: white;
  border-top: 1px solid #ddd;
}

.chat-input {
  flex: 1;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 20px;
  margin-right: 10px;
}

.chat-input-form button {
  padding: 10px 20px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 20px;
  cursor: pointer;
}

.chat-input-form button:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}
```

## Error Handling

### 1. Network Errors
```typescript
const handleNetworkError = (error: any) => {
  if (error.name === 'TypeError' && error.message.includes('fetch')) {
    // Network error - show offline message
    return 'Network error. Please check your connection.';
  }
  return 'An unexpected error occurred. Please try again.';
};
```

### 2. API Errors
```typescript
const handleApiError = async (response: Response) => {
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `HTTP ${response.status}`);
  }
  return response;
};
```

## Best Practices

1. **Session Management**: Always store and reuse session IDs for continuity
2. **Error Handling**: Implement proper error handling for network and API errors
3. **Loading States**: Show loading indicators during API calls
4. **Typing Indicators**: Use WebSocket typing indicators for better UX
5. **Message Persistence**: Store chat history locally or in your app state
6. **Rate Limiting**: Implement client-side rate limiting for message sending
7. **Reconnection**: Implement automatic WebSocket reconnection logic

## Testing

### 1. Test API Endpoints
```bash
# Test chat endpoint
curl -X POST http://localhost:8000/api/v1/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, I need help with visa application"}'

# Test WebSocket connection
wscat -c ws://localhost:8000/api/v1/websocket/ws/test-session
```

### 2. Test Frontend Integration
```typescript
// Test the hook
import { renderHook, act } from '@testing-library/react-hooks';
import { useVisaBot } from './useVisaBot';

test('should send message and receive response', async () => {
  const { result } = renderHook(() => useVisaBot());
  
  await act(async () => {
    await result.current.sendMessage('Hello');
  });
  
  expect(result.current.messages).toHaveLength(2); // User + Bot
  expect(result.current.isLoading).toBe(false);
});
```

This integration guide provides everything you need to connect your React frontend to the VisaBot API. The bot supports both REST API calls for simple interactions and WebSocket connections for real-time chat experiences. 