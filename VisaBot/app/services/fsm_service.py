"""
FSM (Finite State Machine) service for bot state management
"""
from typing import Dict, Any, Optional
from transitions import Machine
from loguru import logger

from app.services.redis_service import redis_client


class VisaBotFSM:
    """Finite State Machine for Visa Bot"""
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.context: Dict[str, Any] = {}
        
        # Define states
        self.states = [
            'greeting',
            'collecting_info',
            'visa_type_selection',
            'document_upload',
            'application_review',
            'payment',
            'confirmation',
            'help',
            'error'
        ]
        
        # Define transitions
        self.transitions = [
            # Greeting transitions
            {'trigger': 'start', 'source': 'greeting', 'dest': 'collecting_info'},
            {'trigger': 'help_request', 'source': 'greeting', 'dest': 'help'},
            
            # Info collection transitions
            {'trigger': 'info_complete', 'source': 'collecting_info', 'dest': 'visa_type_selection'},
            {'trigger': 'back_to_greeting', 'source': 'collecting_info', 'dest': 'greeting'},
            
            # Visa type selection transitions
            {'trigger': 'type_selected', 'source': 'visa_type_selection', 'dest': 'document_upload'},
            {'trigger': 'back_to_info', 'source': 'visa_type_selection', 'dest': 'collecting_info'},
            
            # Document upload transitions
            {'trigger': 'documents_uploaded', 'source': 'document_upload', 'dest': 'application_review'},
            {'trigger': 'back_to_type', 'source': 'document_upload', 'dest': 'visa_type_selection'},
            
            # Application review transitions
            {'trigger': 'review_approved', 'source': 'application_review', 'dest': 'payment'},
            {'trigger': 'review_rejected', 'source': 'application_review', 'dest': 'collecting_info'},
            
            # Payment transitions
            {'trigger': 'payment_complete', 'source': 'payment', 'dest': 'confirmation'},
            {'trigger': 'payment_failed', 'source': 'payment', 'dest': 'error'},
            
            # Error handling transitions
            {'trigger': 'retry', 'source': 'error', 'dest': 'greeting'},
            {'trigger': 'help_request', 'source': '*', 'dest': 'help'},
            {'trigger': 'restart', 'source': '*', 'dest': 'greeting'},
        ]
        
        # Initialize the machine
        self.machine = Machine(
            model=self,
            states=self.states,
            transitions=self.transitions,
            initial='greeting',
            ignore_invalid_triggers=True
        )
    
    def get_state_info(self) -> Dict[str, Any]:
        """Get current state information"""
        return {
            'current_state': self.state,
            'context': self.context,
            'available_triggers': self.machine.get_triggers(self.state)
        }
    
    def update_context(self, key: str, value: Any):
        """Update context data"""
        self.context[key] = value
    
    def get_context(self, key: str, default: Any = None) -> Any:
        """Get context data"""
        return self.context.get(key, default)


class FSMService:
    """FSM service for managing bot state"""
    
    def __init__(self):
        self.fsm_instances: Dict[str, VisaBotFSM] = {}
    
    async def get_fsm(self, session_id: str) -> VisaBotFSM:
        """Get or create FSM instance for session"""
        if session_id not in self.fsm_instances:
            # Try to load from Redis
            state_data = await redis_client.get_state(session_id)
            
            fsm = VisaBotFSM(session_id)
            
            if state_data:
                # Restore state and context
                fsm.state = state_data.get('state', 'greeting')
                fsm.context = state_data.get('context', {})
                logger.info(f"Restored FSM state for session {session_id}: {fsm.state}")
            else:
                logger.info(f"Created new FSM for session {session_id}")
            
            self.fsm_instances[session_id] = fsm
        
        return self.fsm_instances[session_id]
    
    async def save_fsm_state(self, session_id: str):
        """Save FSM state to Redis"""
        if session_id in self.fsm_instances:
            fsm = self.fsm_instances[session_id]
            await redis_client.set_state(
                session_id,
                fsm.state,
                fsm.context
            )
    
    async def transition(self, session_id: str, trigger: str, **kwargs) -> Dict[str, Any]:
        """Execute state transition"""
        fsm = await self.get_fsm(session_id)
        
        # Update context with kwargs
        for key, value in kwargs.items():
            fsm.update_context(key, value)
        
        # Execute transition
        if hasattr(fsm, trigger):
            getattr(fsm, trigger)()
            logger.info(f"Session {session_id}: {trigger} -> {fsm.state}")
        else:
            logger.warning(f"Invalid trigger '{trigger}' for state '{fsm.state}'")
        
        # Save state
        await self.save_fsm_state(session_id)
        
        return fsm.get_state_info()
    
    async def get_current_state(self, session_id: str) -> Dict[str, Any]:
        """Get current state information"""
        fsm = await self.get_fsm(session_id)
        return fsm.get_state_info()
    
    async def reset_session(self, session_id: str):
        """Reset session to initial state"""
        if session_id in self.fsm_instances:
            fsm = self.fsm_instances[session_id]
            fsm.state = 'greeting'
            fsm.context = {}
            await self.save_fsm_state(session_id)
            logger.info(f"Reset session {session_id} to initial state")


# Global FSM service instance
fsm_service = FSMService() 