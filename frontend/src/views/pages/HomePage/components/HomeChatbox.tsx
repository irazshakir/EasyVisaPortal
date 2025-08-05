import React, { useState, useRef, useEffect } from 'react'
import { Input, Button } from '@/components/ui'
import { PiPaperPlaneRightFill, PiQuestionMarkFill, PiArrowClockwiseFill } from 'react-icons/pi'
import visaBotService from '@/services/VisaBotService'

interface Message {
    id: string
    content: string
    isUser: boolean
    timestamp: Date
    sessionId?: string
}

const HomeChatbox = () => {
    const [messages, setMessages] = useState<Message[]>([
        {
            id: '1',
            content: 'Hello! I\'m your Visa Assistant. I can help you with visa applications, requirements, and guidance. How can I assist you today?',
            isUser: false,
            timestamp: new Date()
        }
    ])
    const [newMessage, setNewMessage] = useState('')
    const [isTyping, setIsTyping] = useState(false)
    const [currentSessionId, setCurrentSessionId] = useState<string | null>(null)
    const [error, setError] = useState<string | null>(null)
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
            timestamp: new Date(),
            sessionId: currentSessionId || undefined
        }

        setMessages(prev => [...prev, userMessage])
        setNewMessage('')
        setIsTyping(true)
        setError(null)

        try {
            // Send message to VisaBot using the service
            const response = await visaBotService.sendMessage(newMessage.trim())
            
            // Update session ID if it's a new session
            if (response.session_id && !currentSessionId) {
                setCurrentSessionId(response.session_id)
            }

            // Add bot response to messages
            const botMessage: Message = {
                id: (Date.now() + 1).toString(),
                content: response.message,
                isUser: false,
                timestamp: new Date(response.timestamp),
                sessionId: response.session_id
            }

            setMessages(prev => [...prev, botMessage])
        } catch (error: any) {
            console.error('Error sending message:', error)
            
            // Provide more specific error messages
            let errorMessage = 'Sorry, I encountered an error. Please try again.'
            
            if (error.response?.status === 404) {
                errorMessage = 'VisaBot service is not available. Please try again later.'
            } else if (error.response?.status === 500) {
                errorMessage = 'VisaBot service is experiencing issues. Please try again later.'
            } else if (error.code === 'NETWORK_ERROR' || error.message?.includes('Network Error')) {
                errorMessage = 'Unable to connect to VisaBot. Please check your internet connection.'
            }
            
            setError(errorMessage)
            
            // Add error message to chat
            const errorMsg: Message = {
                id: (Date.now() + 1).toString(),
                content: errorMessage,
                isUser: false,
                timestamp: new Date()
            }
            setMessages(prev => [...prev, errorMsg])
        } finally {
            setIsTyping(false)
        }
    }

    const handleKeyPress = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault()
            handleSendMessage()
        }
    }

    const handleResetSession = async () => {
        if (!currentSessionId) return

        try {
            await visaBotService.resetSession()
            setCurrentSessionId(null)
            setMessages([
                {
                    id: Date.now().toString(),
                    content: 'Hello! I\'m your Visa Assistant. I can help you with visa applications, requirements, and guidance. How can I assist you today?',
                    isUser: false,
                    timestamp: new Date()
                }
            ])
            setError(null)
        } catch (error) {
            console.error('Error resetting session:', error)
            setError('Failed to reset session. Please try again.')
        }
    }

    return (
        <div className="max-w-2xl mx-auto bg-white rounded-lg shadow-lg">
            {/* Chat Header */}
            <div className="bg-primary text-white p-4 rounded-t-lg">
                <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                        <div className="w-10 h-10 bg-white/20 rounded-full flex items-center justify-center">
                            <PiQuestionMarkFill className="w-6 h-6" />
                        </div>
                        <div>
                            <h3 className="font-semibold text-lg">Visa Assistant</h3>
                            <p className="text-sm opacity-90">Ask me anything about visa applications</p>
                        </div>
                    </div>
                    {currentSessionId && (
                        <Button
                            variant="solid"
                            size="sm"
                            onClick={handleResetSession}
                            icon={<PiArrowClockwiseFill />}
                            className="bg-white/20 hover:bg-white/30 text-white"
                        >
                            Reset
                        </Button>
                    )}
                </div>
            </div>

            {/* Error Message */}
            {error && (
                <div className="bg-red-50 border-l-4 border-red-400 p-4">
                    <div className="flex">
                        <div className="flex-shrink-0">
                            <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                            </svg>
                        </div>
                        <div className="ml-3">
                            <p className="text-sm text-red-700">{error}</p>
                        </div>
                    </div>
                </div>
            )}

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
