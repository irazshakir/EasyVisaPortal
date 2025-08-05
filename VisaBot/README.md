# VisaBot - FastAPI + FSM + OpenAI LLM Bot

A sophisticated visa application assistant bot built with FastAPI, Finite State Machine (FSM), and OpenAI's Large Language Model.

## Features

- 🤖 **Intelligent Chat Interface**: Powered by OpenAI's GPT models
- 🔄 **State Management**: Finite State Machine for guided conversations
- 💾 **Session Management**: Redis-backed session storage with PostgreSQL persistence
- 📝 **Conversation History**: Track and manage chat history
- 🔧 **RESTful API**: Clean FastAPI endpoints
- 🌐 **WebSocket Support**: Real-time chat functionality
- 🚀 **Async Support**: High-performance async operations
- 📊 **Health Monitoring**: Built-in health checks
- 🗄️ **Database Integration**: Supabase PostgreSQL support
- 📱 **Frontend Ready**: Complete React integration examples

## Architecture

```
VisaBot/
├── app/
│   ├── api/                    # API endpoints
│   │   ├── routes.py          # Main router
│   │   └── v1/
│   │       ├── __init__.py    # API v1 router
│   │       └── endpoints/
│   │           ├── chat.py     # Chat endpoints
│   │           └── websocket.py # WebSocket endpoints
│   ├── core/                   # Core configuration
│   │   ├── config.py          # Settings
│   │   ├── database.py        # Database connection
│   │   └── events.py          # App events
│   ├── models/                 # Data models
│   │   ├── chat.py            # Chat Pydantic models
│   │   ├── session.py         # Session Pydantic models
│   │   └── database.py        # SQLAlchemy database models
│   ├── services/              # Business logic
│   │   ├── chat_service.py    # Main chat orchestration
│   │   ├── database_service.py # Database operations
│   │   ├── fsm_service.py     # State machine
│   │   ├── openai_service.py  # OpenAI integration
│   │   ├── redis_service.py   # Redis operations
│   │   ├── session_service.py # Session management
│   │   └── websocket_manager.py # WebSocket management
│   └── main.py                # FastAPI app
├── requirements.txt           # Dependencies
├── env.example               # Environment variables
├── start_bot.py              # Startup and test script
├── FRONTEND_INTEGRATION.md   # Frontend integration guide
└── README.md                 # This file
```

## FSM States

The bot operates through these states:

1. **greeting** - Welcome message and initial greeting
2. **ask_country** - Ask user which country visa they're interested in
3. **country_not_supported** - Handle unsupported countries (USA, Canada, UK, Australia, etc.)
4. **ask_profession** - Ask about profession (business person or job holder)
5. **ask_tax_info** - Ask about tax filing and annual income
6. **ask_balance** - Ask about closing balance (2M PKR requirement)
7. **ask_travel** - Ask about previous travel history
8. **evaluation** - Perform visa success ratio evaluation
9. **complete** - Evaluation complete

## Supported Countries

The bot currently supports visa evaluation for **Schengen/European countries**:
- France, Germany, Italy, Spain, Netherlands, Belgium, Switzerland
- Austria, Portugal, Greece, Hungary, Poland, Czech Republic
- Norway, Denmark, Sweden, Finland, Iceland, Luxembourg
- And other Schengen zone countries

**Non-supported countries** (USA, Canada, UK, Australia, etc.) will be informed that only Schengen visa evaluation is available.

## Quick Start

### Prerequisites

- Python 3.8+
- Redis server
- OpenAI API key
- Supabase PostgreSQL database (optional but recommended)

### Installation

1. **Clone and setup**:
   ```bash
   cd VisaBot
   pip install -r requirements.txt
   ```

2. **Environment setup**:
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

3. **Start Redis**:
   ```bash
   # Using Docker
   docker run -d -p 6379:6379 redis:alpine
   
   # Or install locally
   # Follow Redis installation guide for your OS
   ```

4. **Test the setup**:
   ```bash
   python start_bot.py
   ```

5. **Run the bot**:
   ```bash
   python -m uvicorn app.main:app --reload
   ```

6. **Access the API**:
   - API Documentation: http://localhost:8000/docs
   - Chat Endpoint: http://localhost:8000/api/v1/chat
   - WebSocket: ws://localhost:8000/api/v1/websocket/ws/{session_id}

## API Usage

### Start a Chat Session

```bash
curl -X POST "http://localhost:8000/api/v1/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello, I need help with a visa application",
    "context": {}
  }'
```

### Continue Chatting

```bash
curl -X POST "http://localhost:8000/api/v1/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "your-session-id",
    "message": "I want to apply for a tourist visa to France",
    "context": {}
  }'
```

### Get Chat History

```bash
curl "http://localhost:8000/api/v1/chat/history/your-session-id"
```

### WebSocket Connection

```bash
# Using wscat (install with: npm install -g wscat)
wscat -c ws://localhost:8000/api/v1/websocket/ws/your-session-id

# Send a message
{"type": "message", "message": "Hello, I need help with visa application"}
```

## Configuration

Key configuration options in `.env`:

- `OPENAI_API_KEY`: Your OpenAI API key
- `OPENAI_MODEL`: Model to use (default: gpt-4)
- `REDIS_URL`: Redis connection URL
- `DATABASE_URL`: Supabase PostgreSQL connection URL
- `SUPABASE_URL`: Your Supabase project URL
- `SUPABASE_KEY`: Your Supabase anon key
- `BOT_SESSION_TIMEOUT`: Session timeout in seconds
- `MAX_CONVERSATION_HISTORY`: Max messages to keep in history

## Frontend Integration

The VisaBot includes comprehensive frontend integration examples for React applications. See [FRONTEND_INTEGRATION.md](FRONTEND_INTEGRATION.md) for:

- REST API integration with React hooks
- WebSocket real-time chat implementation
- Complete chat component examples
- Error handling and best practices
- Testing strategies

## Development

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black app/
flake8 app/
mypy app/
```

### Database Migrations

```bash
# Create migration
alembic revision --autogenerate -m "Initial migration"

# Apply migration
alembic upgrade head
```

### Docker Support

```bash
# Build image
docker build -t visabot .

# Run container
docker run -p 8000:8000 --env-file .env visabot
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Support

For issues and questions, please open an issue on GitHub. 