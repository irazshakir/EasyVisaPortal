// Simple test script to verify VisaBot API endpoints
// Run this with Node.js to test the API connection

const axios = require('axios');

const API_BASE_URL = 'http://localhost:8000/api/v1/chat';

async function testVisaBotAPI() {
    console.log('🧪 Testing VisaBot API endpoints...\n');

    try {
        // Test 1: Send a message
        console.log('1. Testing POST /chat/ - Send message');
        const messageResponse = await axios.post(API_BASE_URL, {
            message: 'Hello, I need help with a tourist visa application.'
        });
        console.log('✅ Message sent successfully');
        console.log('Response:', {
            session_id: messageResponse.data.session_id,
            message: messageResponse.data.message.substring(0, 100) + '...',
            state: messageResponse.data.state
        });
        console.log('');

        const sessionId = messageResponse.data.session_id;

        // Test 2: Get session status
        console.log('2. Testing GET /chat/status/{session_id} - Get session status');
        const statusResponse = await axios.get(`${API_BASE_URL}/status/${sessionId}`);
        console.log('✅ Session status retrieved successfully');
        console.log('Status:', statusResponse.data);
        console.log('');

        // Test 3: Get chat history
        console.log('3. Testing GET /chat/history/{session_id} - Get chat history');
        const historyResponse = await axios.get(`${API_BASE_URL}/history/${sessionId}`);
        console.log('✅ Chat history retrieved successfully');
        console.log('History length:', historyResponse.data.history.length);
        console.log('');

        // Test 4: Send another message
        console.log('4. Testing POST /chat/ - Send follow-up message');
        const followUpResponse = await axios.post(API_BASE_URL, {
            session_id: sessionId,
            message: 'What documents do I need for a tourist visa?'
        });
        console.log('✅ Follow-up message sent successfully');
        console.log('Response:', {
            session_id: followUpResponse.data.session_id,
            message: followUpResponse.data.message.substring(0, 100) + '...',
            state: followUpResponse.data.state
        });
        console.log('');

        // Test 5: List active sessions
        console.log('5. Testing GET /chat/sessions - List active sessions');
        const sessionsResponse = await axios.get(`${API_BASE_URL}/sessions`);
        console.log('✅ Active sessions retrieved successfully');
        console.log('Active sessions:', sessionsResponse.data.sessions.length);
        console.log('');

        console.log('🎉 All API tests passed successfully!');
        console.log('The VisaBot backend is working correctly.');

    } catch (error) {
        console.error('❌ API test failed:');
        if (error.response) {
            console.error('Status:', error.response.status);
            console.error('Data:', error.response.data);
        } else if (error.request) {
            console.error('Request error:', error.message);
            console.error('Make sure the VisaBot backend is running on http://localhost:8000');
        } else {
            console.error('Error:', error.message);
        }
    }
}

// Run the test
testVisaBotAPI(); 