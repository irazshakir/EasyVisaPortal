# Visa Evaluation Bot

A sophisticated FastAPI-based visa evaluation bot that uses Finite State Machine (FSM) and OpenAI to guide users through a comprehensive visa eligibility assessment.

## 🎯 Features

- **FSM-Driven Conversation Flow**: Structured 6-stage evaluation process
- **OpenAI Integration**: Intelligent parsing of user responses and contextual replies
- **Session Management**: Persistent session state with Redis and in-memory storage
- **Comprehensive Evaluation**: Multi-factor scoring system for visa eligibility
- **RESTful API**: Complete FastAPI endpoints for bot interaction

## 🏗️ Architecture

### Core Components

1. **FSM Service** (`fsm_service.py`)
   - Manages conversation flow through 6 defined states
   - Handles state transitions and data collection
   - Performs final evaluation with scoring algorithm

2. **OpenAI Service** (`openai_service.py`)
   - Parses user input using GPT models
   - Extracts structured data from natural language
   - Generates contextual responses

3. **Session Service** (`session_service.py`)
   - Manages user sessions and state persistence
   - Stores conversation history
   - Handles session lifecycle

4. **Chat Service** (`chat_service.py`)
   - Orchestrates all services
   - Main entry point for bot interactions
   - Handles error management and response formatting

## 📋 Evaluation Stages

The bot follows a 6-stage FSM flow:

1. **ASK_PROFESSION** → "Are you a business person or job holder?"
2. **ASK_TAX_INFO** → "Are you a tax filer? If yes, what was your annual income?"
3. **ASK_BALANCE** → "Can you manage a closing balance of 2 million PKR?"
4. **ASK_TRAVEL** → "What is your previous travel history in the last 5 years?"
5. **EVALUATION** → Automatic evaluation and scoring
6. **COMPLETE** → Final results and recommendations

## 🎯 Evaluation Criteria

The bot evaluates visa eligibility based on:

- **Professional Status** (20 points): Business person or job holder
- **Financial Profile** (30 points): Tax filing status and annual income > 1.2M PKR
- **Financial Capacity** (25 points): Closing balance >= 1.5-2M PKR
- **Travel History** (25 points): Previous international travel experience

### Scoring System
- **70+ points**: Highly eligible - Proceed with application
- **50-69 points**: Eligible - Apply with additional documentation
- **<50 points**: Not eligible - Improve profile first

## 🚀 Quick Start

### 1. Environment Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export OPENAI_API_KEY="your_openai_api_key"
export REDIS_URL="redis://localhost:6379"
```

### 2. Run the Application

```bash
# Start the FastAPI server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Test the Bot

```bash
# Run the test script
python test_visa_bot.py
```

## 📡 API Endpoints

### Chat Interaction
```http
POST /api/v1/chat/
Content-Type: application/json

{
    "session_id": "optional_session_id",
    "message": "I am a business person"
}
```

### Session Management
```http
GET /api/v1/chat/status/{session_id}
POST /api/v1/chat/reset/{session_id}
GET /api/v1/chat/evaluation/{session_id}
GET /api/v1/chat/history/{session_id}
GET /api/v1/chat/sessions
DELETE /api/v1/chat/session/{session_id}
```

## 💬 Example Conversation Flow

```
👤 User: I am a business person
🤖 Bot: Thank you for your response. Are you a tax filer? If yes, what was your annual income in the last tax return?

👤 User: Yes, I am a tax filer. My annual income was 1.5 million PKR
🤖 Bot: Thank you for your response. Can you manage a closing balance of 2 million PKR?

👤 User: Yes, I can manage a closing balance of 2.5 million PKR
🤖 Bot: Thank you for your response. What is your previous travel history in the last 5 years?

👤 User: Yes, I have traveled to USA and UK in the last 5 years
🤖 Bot: 📋 **VISA EVALUATION REPORT**
     **Overall Score:** 100/100 (100.0%)
     ✅ **RECOMMENDATION: ELIGIBLE**
     **Strengths:**
     • ✅ Good professional background
     • ✅ Strong financial profile with tax compliance
     • ✅ Sufficient financial reserves
     • ✅ Strong travel history
     **Next Steps:**
     • Proceed with visa application
     • Prepare required documents
```

## 🔧 Configuration

### Environment Variables

```env
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-4
OPENAI_MAX_TOKENS=2000
OPENAI_TEMPERATURE=0.7

# Redis Configuration
REDIS_URL=redis://localhost:6379
REDIS_DB=0

# Bot Configuration
BOT_SESSION_TIMEOUT=3600
MAX_CONVERSATION_HISTORY=10
```

### Customization

You can customize the evaluation criteria by modifying:

1. **Scoring weights** in `fsm_service.py` - `evaluate_profile()` method
2. **Questions** in `fsm_service.py` - `questions` dictionary
3. **Parsing logic** in `openai_service.py` - `_parse_*_input()` methods
4. **Response generation** in `openai_service.py` - `generate_response_for_state()` method

## 🧪 Testing

### Unit Tests
```bash
# Run tests
pytest tests/

# Run specific test
pytest tests/test_chat_service.py
```

### Integration Test
```bash
# Run the demo script
python test_visa_bot.py
```

## 📊 Monitoring

The bot provides comprehensive logging and monitoring:

- **Session tracking**: Monitor active sessions and progress
- **Evaluation analytics**: Track success rates and scoring patterns
- **Error handling**: Detailed error logs for debugging
- **Performance metrics**: Response times and API usage

## 🔒 Security

- **Session isolation**: Each user gets a unique session ID
- **Input validation**: All user inputs are validated and sanitized
- **Rate limiting**: Built-in protection against abuse
- **Secure storage**: Sensitive data encrypted in Redis

## 🚀 Deployment

### Docker Deployment
```bash
# Build and run with Docker
docker build -t visa-bot .
docker run -p 8000:8000 visa-bot
```

### Kubernetes Deployment
```bash
# Deploy to Kubernetes
kubectl apply -f infrastructure/kubernetes/
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the documentation
- Review the test examples

---

**Built with ❤️ using FastAPI, OpenAI, and Redis** 