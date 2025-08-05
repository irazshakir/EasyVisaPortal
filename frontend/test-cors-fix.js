// Test script to verify CORS fix
// Run this in the browser console or as a Node.js script

async function testCorsFix() {
    console.log('🧪 Testing CORS fix...\n');

    try {
        // Test 1: Test endpoint
        console.log('1. Testing GET /api/v1/chat/test');
        const testResponse = await fetch('http://localhost:8000/api/v1/chat/test', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'omit' // Don't send credentials
        });
        
        if (testResponse.ok) {
            const testData = await testResponse.json();
            console.log('✅ Test endpoint working:', testData);
        } else {
            console.log('❌ Test endpoint failed:', testResponse.status);
        }
        console.log('');

        // Test 2: Send a message
        console.log('2. Testing POST /api/v1/chat/');
        const messageResponse = await fetch('http://localhost:8000/api/v1/chat/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'omit', // Don't send credentials
            body: JSON.stringify({
                message: 'Hello, this is a test message.'
            })
        });
        
        if (messageResponse.ok) {
            const messageData = await messageResponse.json();
            console.log('✅ Message sent successfully:', {
                session_id: messageData.session_id,
                message: messageData.message.substring(0, 100) + '...',
                state: messageData.state
            });
        } else {
            console.log('❌ Message failed:', messageResponse.status);
            const errorData = await messageResponse.text();
            console.log('Error details:', errorData);
        }
        console.log('');

        console.log('🎉 CORS test completed!');

    } catch (error) {
        console.error('❌ Test failed:', error);
        console.error('Make sure the VisaBot backend is running on http://localhost:8000');
    }
}

// Run the test
testCorsFix(); 