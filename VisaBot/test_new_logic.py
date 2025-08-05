#!/usr/bin/env python3
"""
Test script for the new greeting and country selection logic
"""
import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.services.fsm_service import VisaEvaluationFSM, FSMStates

def test_fsm_logic():
    """Test the new FSM logic with different scenarios"""
    
    print("=== Testing New FSM Logic ===\n")
    
    # Test 1: Initial greeting
    print("Test 1: Initial greeting")
    fsm = VisaEvaluationFSM("test_session_1")
    print(f"Initial state: {fsm.current_state.value}")
    print(f"Initial question: {fsm.get_current_question()}")
    print()
    
    # Test 2: Supported country (France)
    print("Test 2: Supported country (France)")
    next_state, next_question = fsm.get_next_state(fsm.current_state, "France")
    print(f"User input: 'France'")
    print(f"Next state: {next_state.value}")
    print(f"Next question: {next_question}")
    print(f"Selected country: {fsm.answers.get('selected_country', 'Not set')}")
    print()
    
    # Test 3: Non-supported country (USA)
    print("Test 3: Non-supported country (USA)")
    fsm2 = VisaEvaluationFSM("test_session_2")
    # Move to ask_country state
    fsm2.current_state = FSMStates.ASK_COUNTRY
    next_state, next_question = fsm2.get_next_state(fsm2.current_state, "USA")
    print(f"User input: 'USA'")
    print(f"Next state: {next_state.value}")
    print(f"Next question: {next_question}")
    print(f"Unsupported country: {fsm2.answers.get('unsupported_country', 'Not set')}")
    print()
    
    # Test 4: User wants to try Schengen after being told USA is not supported
    print("Test 4: User wants to try Schengen")
    fsm2.current_state = FSMStates.COUNTRY_NOT_SUPPORTED
    next_state, next_question = fsm2.get_next_state(fsm2.current_state, "Yes, I want to try Schengen")
    print(f"User input: 'Yes, I want to try Schengen'")
    print(f"Next state: {next_state.value}")
    print(f"Next question: {next_question}")
    print()
    
    # Test 5: User declines Schengen offer
    print("Test 5: User declines Schengen offer")
    fsm3 = VisaEvaluationFSM("test_session_3")
    fsm3.current_state = FSMStates.COUNTRY_NOT_SUPPORTED
    next_state, next_question = fsm3.get_next_state(fsm3.current_state, "No, I'm not interested")
    print(f"User input: 'No, I'm not interested'")
    print(f"Next state: {next_state.value}")
    print(f"Next question: {next_question}")
    print()
    
    # Test 6: Various supported countries
    print("Test 6: Testing various supported countries")
    supported_countries = ["Germany", "Italy", "Spain", "Netherlands", "Switzerland", "Europe", "Schengen"]
    for country in supported_countries:
        fsm_test = VisaEvaluationFSM(f"test_session_{country}")
        fsm_test.current_state = FSMStates.ASK_COUNTRY
        next_state, _ = fsm_test.get_next_state(fsm_test.current_state, country)
        print(f"'{country}' -> {next_state.value}")
    print()
    
    # Test 7: Various non-supported countries
    print("Test 7: Testing various non-supported countries")
    non_supported_countries = ["USA", "Canada", "UK", "Australia", "Japan", "Singapore"]
    for country in non_supported_countries:
        fsm_test = VisaEvaluationFSM(f"test_session_{country}")
        fsm_test.current_state = FSMStates.ASK_COUNTRY
        next_state, _ = fsm_test.get_next_state(fsm_test.current_state, country)
        print(f"'{country}' -> {next_state.value}")
    print()
    
    print("=== Test Complete ===")

if __name__ == "__main__":
    test_fsm_logic() 