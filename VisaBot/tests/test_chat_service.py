"""
Tests for chat service
"""
import pytest
from unittest.mock import AsyncMock, patch
from app.services.chat_service import ChatService
from app.models.chat import ChatResponse


@pytest.mark.asyncio
async def test_process_message_success():
    """Test successful message processing"""
    with patch('app.services.chat_service.fsm_service') as mock_fsm, \
         patch('app.services.chat_service.OpenAIService') as mock_openai, \
         patch('app.services.chat_service.SessionService') as mock_session:
        
        # Setup mocks
        mock_fsm.get_current_state.return_value = {
            'current_state': 'greeting',
            'context': {}
        }
        
        mock_openai_instance = AsyncMock()
        mock_openai_instance.analyze_intent.return_value = {
            'intent': 'greeting',
            'confidence': 0.9,
            'entities': {},
            'requires_action': False,
            'next_state': 'greeting'
        }
        mock_openai_instance.generate_response.return_value = "Hello! How can I help you with your visa application?"
        mock_openai.return_value = mock_openai_instance
        
        mock_session_instance = AsyncMock()
        mock_session.return_value = mock_session_instance
        
        # Create service and test
        service = ChatService()
        response = await service.process_message(
            session_id="test-session",
            message="Hello",
            context={}
        )
        
        # Assertions
        assert isinstance(response, ChatResponse)
        assert response.session_id == "test-session"
        assert response.state == "greeting"
        assert "Hello" in response.message


@pytest.mark.asyncio
async def test_process_message_error():
    """Test error handling in message processing"""
    with patch('app.services.chat_service.fsm_service') as mock_fsm:
        mock_fsm.get_current_state.side_effect = Exception("Test error")
        
        service = ChatService()
        response = await service.process_message(
            session_id="test-session",
            message="Hello",
            context={}
        )
        
        assert response.state == "error"
        assert "error" in response.message.lower() 