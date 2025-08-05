# VisaBot Frontend Integration

This document explains how the frontend is connected to the VisaBot backend.

## Overview

The frontend now includes a complete integration with the VisaBot backend, which provides:
- Real-time chat with the VisaBot AI assistant
- Session management for ongoing conversations
- Error handling and user feedback
- Reset functionality to start new conversations

## Architecture

### Components

1. **HomeChatbox** (`src/views/pages/HomePage/components/HomeChatbox.tsx`)
   - Main chat interface component
   - Handles user input and displays messages
   - Manages session state and error handling

2. **VisaBot API** (`src/views/pages/HomePage/api/visaBotapi.ts`)
   - Direct API client for VisaBot endpoints
   - TypeScript interfaces for all API requests/responses
   - Handles HTTP communication with the backend

3. **VisaBot Service** (`src/services/VisaBotService.ts`)
   - High-level service layer for VisaBot operations
   - Manages session state and provides clean API
   - Handles session lifecycle (create, reset, end)

### API Endpoints

The frontend connects to these VisaBot endpoints:

- `POST /api/v1/chat/` - Send a message and get response
- `GET /api/v1/chat/status/{session_id}` - Get session status
- `POST /api/v1/chat/reset/{session_id}` - Reset session
- `GET /api/v1/chat/evaluation/{session_id}` - Get evaluation summary
- `GET /api/v1/chat/history/{session_id}` - Get chat history
- `GET /api/v1/chat/sessions` - List active sessions
- `DELETE /api/v1/chat/session/{session_id}` - End session

## Configuration

### API URL Configuration

The frontend is configured to connect to the VisaBot backend through:

1. **Vite Proxy** (`vite.config.ts`):
   ```typescript
   server: {
     proxy: {
       '/api': {
         target: 'http://localhost:8000',
         changeOrigin: true,
         secure: false
       }
     }
   }
   ```

2. **Axios Base Configuration** (`src/services/axios/AxiosBase.ts`):
   ```typescript
   const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'
   ```

### CORS Configuration

The VisaBot backend is configured to allow all origins:
```python
ALLOWED_HOSTS: List[str] = ["*"]
```

## Usage

### Starting the Services

1. **Start VisaBot Backend**:
   ```bash
   cd VisaBot
   python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

2. **Start Frontend Development Server**:
   ```bash
   cd frontend
   npm run dev
   ```

### Testing the Integration

1. Navigate to the homepage (`/`)
2. You should see the VisaBot chat interface
3. Type a message and press Enter or click Send
4. The message should be sent to the VisaBot backend
5. You should receive a response from the AI assistant

### Error Handling

The integration includes comprehensive error handling:

- **Network Errors**: Shows "Unable to connect to VisaBot" message
- **404 Errors**: Shows "VisaBot service is not available" message
- **500 Errors**: Shows "VisaBot service is experiencing issues" message
- **Generic Errors**: Shows generic error message with retry option

### Session Management

- Each conversation maintains a session ID
- Sessions persist until reset or timeout
- Users can reset the conversation using the Reset button
- Session state is managed automatically by the VisaBotService

## Troubleshooting

### Common Issues

1. **CORS Errors**:
   - Ensure VisaBot backend is running on port 8000
   - Check that CORS is properly configured in the backend
   - Verify the proxy configuration in vite.config.ts

2. **Connection Refused**:
   - Make sure VisaBot backend is running
   - Check if the port 8000 is available
   - Verify the API URL configuration

3. **Authentication Errors**:
   - The chat endpoints don't require authentication
   - Check that `skipAuthHeader: true` is set in API calls

### Debug Mode

To enable debug logging:

1. Set `VITE_APP_DEBUG=true` in environment variables
2. Check browser console for detailed error messages
3. Check VisaBot backend logs for server-side errors

## Future Enhancements

Potential improvements for the integration:

1. **WebSocket Support**: Real-time messaging without polling
2. **File Upload**: Support for document uploads in chat
3. **Session Persistence**: Save sessions in localStorage
4. **Typing Indicators**: Show when the bot is processing
5. **Message History**: Load previous conversations
6. **Evaluation Display**: Show visa evaluation results in UI 