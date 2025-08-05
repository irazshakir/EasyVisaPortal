# Greeting and Country Selection Implementation

## Overview

This document describes the implementation of the new greeting and country selection logic for the VisaBot. The bot now starts with a greeting and routes users based on their country of interest.

## New Features

### 1. Greeting Flow
- **Initial State**: The bot now starts with a `GREETING` state instead of directly asking profession
- **Welcome Message**: "Welcome to Easy Visa PK free visa success ratio evaluation. I am here to assist and answer your questions. Which Country visa are you interested to apply?"

### 2. Country Selection Logic
- **ASK_COUNTRY State**: After greeting, the bot asks which country visa the user is interested in
- **Country Classification**: Countries are classified into supported and non-supported categories

### 3. Supported Countries (Schengen/Europe)
The bot supports visa evaluation for:
- **Major Schengen Countries**: France, Germany, Italy, Spain, Netherlands, Belgium, Switzerland
- **Other European Countries**: Austria, Portugal, Greece, Hungary, Poland, Czech Republic, Norway, Denmark, Sweden, Finland, Iceland, Luxembourg, Slovenia, Slovakia, Estonia, Latvia, Lithuania, Malta, Liechtenstein, Croatia, Romania, Cyprus

### 4. Non-Supported Countries
The bot informs users that it doesn't support:
- **Major Countries**: USA, Canada, UK, Australia, New Zealand
- **Asian Countries**: Japan, Singapore, Malaysia, Thailand, China, India, Pakistan, Bangladesh, Sri Lanka, Nepal, Bhutan, Maldives, Afghanistan, Iran, Iraq, Syria, Lebanon, Jordan, Israel, Palestine
- **African Countries**: Egypt, Libya, Tunisia, Algeria, Morocco, and many others
- **Other Regions**: Various countries from different continents

### 5. User Experience Flow

#### Scenario 1: User wants Schengen visa
1. Bot greets user
2. User mentions "France" (or any supported country)
3. Bot confirms and starts evaluation questions
4. Bot proceeds with profession, tax, balance, and travel questions
5. Bot provides evaluation

#### Scenario 2: User wants non-Schengen visa
1. Bot greets user
2. User mentions "USA" (or any non-supported country)
3. Bot informs that only Schengen visas are supported
4. Bot offers to evaluate for a Schengen country instead
5. If user accepts: Bot asks for Schengen country preference
6. If user declines: Bot ends conversation politely

## Technical Implementation

### FSM States Updated
```python
class FSMStates(Enum):
    GREETING = "greeting"                    # NEW
    ASK_COUNTRY = "ask_country"             # NEW
    COUNTRY_NOT_SUPPORTED = "country_not_supported"  # NEW
    ASK_PROFESSION = "ask_profession"
    ASK_TAX_INFO = "ask_tax_info"
    ASK_BALANCE = "ask_balance"
    ASK_TRAVEL = "ask_travel"
    EVALUATION = "evaluation"
    COMPLETE = "complete"
```

### Key Methods Added
- `_is_supported_country()`: Checks if user input indicates a supported country
- `_is_non_supported_country()`: Checks if user input indicates a non-supported country
- Updated `get_next_state()`: Handles the new flow logic

### Files Modified
1. **`app/services/fsm_service.py`**: Added new states and country detection logic
2. **`app/services/chat_service.py`**: Updated progress calculation and reset logic
3. **`app/services/session_service.py`**: Updated initial state to GREETING
4. **`README.md`**: Updated documentation

## Testing

### Test Files Created
1. **`test_new_logic.py`**: Tests the FSM logic with various scenarios
2. **`test_integration.py`**: Tests the complete chat flow integration

### Test Scenarios Covered
- Initial greeting flow
- Supported country responses
- Non-supported country responses
- User acceptance/decline of Schengen offer
- Various country name variations

## Usage Examples

### Example 1: Successful Schengen Flow
```
User: "Hello"
Bot: "Welcome to Easy Visa PK free visa success ratio evaluation. I am here to assist and answer your questions. Which Country visa are you interested to apply?"

User: "France"
Bot: "Great! I'm going to ask you some questions to evaluate your success ratio. Are you a business person or job holder?"
```

### Example 2: Non-Supported Country Flow
```
User: "Hello"
Bot: "Welcome to Easy Visa PK free visa success ratio evaluation. I am here to assist and answer your questions. Which Country visa are you interested to apply?"

User: "USA"
Bot: "At the moment we are not providing Visa Success ratio evaluation for this country. We are only assisting in Schengen visas. Would you like to evaluate for a Schengen country instead?"

User: "Yes, I want to try Schengen"
Bot: "Great! Which Schengen country would you like to evaluate for? (e.g., France, Germany, Italy, Spain, etc.)"
```

## Benefits

1. **Better User Experience**: Clear greeting and guidance
2. **Focused Service**: Only handles supported visa types
3. **Graceful Handling**: Politely redirects users interested in non-supported countries
4. **Extensible**: Easy to add more supported countries in the future
5. **Consistent Flow**: Maintains the existing evaluation logic for supported countries

## Future Enhancements

1. **Add More Countries**: Extend support to other visa types
2. **Country-Specific Questions**: Customize questions based on selected country
3. **Multi-Language Support**: Support for different languages
4. **Visa Type Selection**: Allow users to choose specific visa types (tourist, business, student, etc.) 