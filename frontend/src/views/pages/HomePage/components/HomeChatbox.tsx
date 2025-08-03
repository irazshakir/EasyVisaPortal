import React, { useState, useRef, useEffect } from 'react'
import { Input, Button } from '@/components/ui'
import { PiPaperPlaneRightFill, PiQuestionMarkFill } from 'react-icons/pi'

interface Message {
    id: string
    content: string
    isUser: boolean
    timestamp: Date
}

const HomeChatbox = () => {
    const [messages, setMessages] = useState<Message[]>([
        {
            id: '1',
            content: 'Hello! I\'m here to help you with your visa queries. How can I assist you today?',
            isUser: false,
            timestamp: new Date()
        }
    ])
    const [newMessage, setNewMessage] = useState('')
    const [isTyping, setIsTyping] = useState(false)
    const messagesEndRef = useRef<HTMLDivElement>(null)

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
    }

    useEffect(() => {
        scrollToBottom()
    }, [messages])

    const handleSendMessage = async () => {
        if (!newMessage.trim()) return

        const userMessage: Message = {
            id: Date.now().toString(),
            content: newMessage.trim(),
            isUser: true,
            timestamp: new Date()
        }

        setMessages(prev => [...prev, userMessage])
        setNewMessage('')
        setIsTyping(true)

        // Simulate AI response
        setTimeout(() => {
            const aiResponse: Message = {
                id: (Date.now() + 1).toString(),
                content: getAIResponse(newMessage.trim()),
                isUser: false,
                timestamp: new Date()
            }
            setMessages(prev => [...prev, aiResponse])
            setIsTyping(false)
        }, 1000)
    }

    const handleKeyPress = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault()
            handleSendMessage()
        }
    }

    const getAIResponse = (userMessage: string): string => {
        const lowerMessage = userMessage.toLowerCase()
        
        if (lowerMessage.includes('visa type') || lowerMessage.includes('what visa')) {
            return 'We offer various visa types including Tourist Visa, Business Visa, Student Visa, and Work Visa. Which type are you interested in?'
        }
        
        if (lowerMessage.includes('document') || lowerMessage.includes('required')) {
            return 'Common documents required include: Passport, Photos, Application Form, Financial Statements, and Travel Insurance. The specific requirements depend on your visa type.'
        }
        
        if (lowerMessage.includes('process') || lowerMessage.includes('how long')) {
            return 'The visa processing time typically ranges from 3-15 business days depending on the visa type and your application completeness. We recommend applying at least 2 weeks before your travel date.'
        }
        
        if (lowerMessage.includes('fee') || lowerMessage.includes('cost')) {
            return 'Visa fees vary by type: Tourist Visa ($50-150), Business Visa ($100-200), Student Visa ($150-300). You can check the exact fee on our application portal.'
        }
        
        if (lowerMessage.includes('track') || lowerMessage.includes('status')) {
            return 'You can track your application status by logging into your account or using the tracking number provided in your confirmation email.'
        }
        
        if (lowerMessage.includes('help') || lowerMessage.includes('support')) {
            return 'Our support team is available 24/7. You can contact us via email at support@evisa.com or call our helpline at +1-800-VISA-HELP.'
        }
        
        return 'Thank you for your question! For detailed information about visa requirements, processing times, and fees, please visit our application portal or contact our support team. How else can I help you?'
    }

    return (
        <div className="max-w-2xl mx-auto bg-white rounded-lg shadow-lg">
            {/* Chat Header */}
            <div className="bg-primary text-white p-4 rounded-t-lg">
                <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 bg-white/20 rounded-full flex items-center justify-center">
                        <PiQuestionMarkFill className="w-6 h-6" />
                    </div>
                    <div>
                        <h3 className="font-semibold text-lg">Visa Assistant</h3>
                        <p className="text-sm opacity-90">Ask me anything about visa applications</p>
                    </div>
                </div>
            </div>

            {/* Messages Area */}
            <div className="h-96 overflow-y-auto p-4 space-y-4">
                {messages.map((message) => (
                    <div
                        key={message.id}
                        className={`flex ${message.isUser ? 'justify-end' : 'justify-start'}`}
                    >
                        <div
                            className={`max-w-[80%] rounded-2xl p-3 ${
                                message.isUser
                                    ? 'bg-primary text-white'
                                    : 'bg-gray-100 text-gray-900'
                            }`}
                        >
                            <p className="text-sm">{message.content}</p>
                            <p className={`text-xs mt-1 ${
                                message.isUser ? 'text-white/70' : 'text-gray-500'
                            }`}>
                                {message.timestamp.toLocaleTimeString([], { 
                                    hour: '2-digit', 
                                    minute: '2-digit' 
                                })}
                            </p>
                        </div>
                    </div>
                ))}
                
                {isTyping && (
                    <div className="flex justify-start">
                        <div className="bg-gray-100 text-gray-900 rounded-2xl p-3">
                            <div className="flex space-x-1">
                                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                            </div>
                        </div>
                    </div>
                )}
                
                <div ref={messagesEndRef} />
            </div>

            {/* Input Area */}
            <div className="p-4 border-t border-gray-200">
                <div className="flex items-center space-x-2">
                    <Input
                        value={newMessage}
                        onChange={(e) => setNewMessage(e.target.value)}
                        onKeyPress={handleKeyPress}
                        placeholder="Type your visa question..."
                        className="flex-grow"
                        disabled={isTyping}
                    />
                    <Button
                        variant="solid"
                        onClick={handleSendMessage}
                        disabled={!newMessage.trim() || isTyping}
                        icon={<PiPaperPlaneRightFill />}
                    >
                        Send
                    </Button>
                </div>
            </div>
        </div>
    )
}

export default HomeChatbox
