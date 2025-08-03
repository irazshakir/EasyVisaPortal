import { useState, useEffect } from 'react'
import { Avatar, Input, Notification, Button } from '@/components/ui'
import classNames from '@/utils/classNames'
import { chatApi, ChatUser } from '../api/chatApi'
import toast from '@/components/ui/toast'
import { useWebSocket } from '@/contexts/WebSocketContext'

interface ChatListProps {
    onSelectUser: (user: { id: string; name: string; phoneNumber: string; wa_id?: string }) => void
}

// Phone number utilities
const PhoneUtils = {
    // Get last 10 digits of a phone number
    normalize: (phone: string): string => {
        const digits = (phone || '').replace(/\D/g, '')
        return digits.slice(-10)
    },
    
    // Format phone number with + prefix
    format: (phone: string): string => {
        const digits = (phone || '').replace(/\D/g, '')
        return digits ? `+${digits}` : ''
    },
    
    // Check if numbers match by last 10 digits
    matches: (chat: ChatUser, phoneNumber: string): boolean => {
        const normalizedIncoming = PhoneUtils.normalize(phoneNumber)
        const normalizedPhone = PhoneUtils.normalize(chat.phoneNumber)
        const normalizedWaId = chat.wa_id ? PhoneUtils.normalize(chat.wa_id) : ''
        
        // Match either by phone number or wa_id
        return normalizedPhone === normalizedIncoming || 
               normalizedWaId === normalizedIncoming
    }
}

const getInitials = (name: string) => {
    const names = name.split(' ')
    return names.map(n => n[0]).join('').toUpperCase()
}

// Add utility functions for date formatting
const formatDateTime = (timestamp: string | null | undefined): string => {
    if (!timestamp) return ''
    
    const date = new Date(timestamp)
    const now = new Date()
    const yesterday = new Date(now)
    yesterday.setDate(yesterday.getDate() - 1)
    
    // If message is from today, show only time
    if (date.toDateString() === now.toDateString()) {
        return date.toLocaleTimeString('en-US', { 
            hour: 'numeric', 
            minute: '2-digit',
            hour12: true 
        })
    }
    
    // If message is from yesterday, show "Yesterday"
    if (date.toDateString() === yesterday.toDateString()) {
        return 'Yesterday'
    }
    
    // If message is from this year, show date without year
    if (date.getFullYear() === now.getFullYear()) {
        return date.toLocaleDateString('en-US', { 
            month: 'short', 
            day: 'numeric' 
        })
    }
    
    // For older messages, show full date
    return date.toLocaleDateString('en-US', { 
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    })
}

const ChatList = ({ onSelectUser }: ChatListProps) => {
    const [chats, setChats] = useState<ChatUser[]>([])
    const [loading, setLoading] = useState(false)
    const [searchTerm, setSearchTerm] = useState('')
    const { lastMessage, connectionStatus } = useWebSocket()

    useEffect(() => {
        console.log('ChatList: Initial load')
        loadChats()
    }, [])

    // Log connection status changes
    useEffect(() => {
        console.log('ChatList: WebSocket connection status:', connectionStatus)
        if (connectionStatus === 'connected') {
            console.log('ChatList: WebSocket connection established')
        }
    }, [connectionStatus])

    // Handle incoming WebSocket messages
    useEffect(() => {
        if (lastMessage?.type === 'whatsapp.message' && lastMessage.message) {
            console.log('ChatList: Processing WhatsApp message:', lastMessage.message)
            handleWebSocketMessage(lastMessage.message)
        }
    }, [lastMessage])

    const loadChats = async () => {
        setLoading(true)
        try {
            console.log('ChatList: Loading chats')
            const response = await chatApi.getWhatsAppChats()
            if (response?.data) {
                console.log('ChatList: Raw API response:', response.data)
                const chatMap = new Map<string, ChatUser>()
                
                response.data.forEach(chat => {
                    // Use last 10 digits as key for chat map
                    const normalizedPhone = PhoneUtils.normalize(chat.phoneNumber)
                    const formattedChat = {
                        ...chat,
                        // Preserve original ID and wa_id
                        phoneNumber: PhoneUtils.format(chat.phoneNumber),
                        wa_id: chat.wa_id || chat.phoneNumber, // Ensure wa_id is preserved
                        timestamp: formatDateTime(chat.timestamp),
                        lastMessage: chat.lastMessage 
                            ? chat.lastMessage.length > 40 
                                ? `${chat.lastMessage.substring(0, 40)}...` 
                                : chat.lastMessage
                            : ''
                    }
                    
                    console.log('ChatList: Formatted chat:', {
                        id: formattedChat.id,
                        phoneNumber: formattedChat.phoneNumber,
                        wa_id: formattedChat.wa_id
                    })
                    
                    const existingChat = chatMap.get(normalizedPhone)
                    if (existingChat) {
                        const existingTime = new Date(chat.timestamp || 0).getTime()
                        const newTime = new Date(chat.timestamp || 0).getTime()
                        if (newTime > existingTime) {
                            chatMap.set(normalizedPhone, formattedChat)
                        }
                    } else {
                        chatMap.set(normalizedPhone, formattedChat)
                    }
                })

                const uniqueChats = Array.from(chatMap.values())
                    .sort((a, b) => {
                        const timeA = new Date(a.timestamp || 0).getTime()
                        const timeB = new Date(b.timestamp || 0).getTime()
                        return timeB - timeA
                    })

                console.log('ChatList: Loaded unique chats:', uniqueChats)
                setChats(uniqueChats)
            }
        } catch (error) {
            console.error('ChatList: Failed to load chats:', error)
            toast.push(
                <Notification title="Error" type="danger">
                    Failed to load chats
                </Notification>
            )
        } finally {
            setLoading(false)
        }
    }

    const handleWebSocketMessage = (message: any) => {
        console.log('ChatList: Processing message for chat update:', message)
        
        // Extract message details with proper fallbacks
        const messageId = message.id || message.message_id
        const messageContent = message.content || message.text?.body || message.text || ''
        const phoneNumber = (message.phone_number || message.from || '').replace(/^\+/, '')
        const chatName = message.chat_name || message.sender?.name || 'Unknown'
        const timestamp = message.timestamp
        
        // Update chats when a new message is received
        setChats(prevChats => {
            // Find existing chat with normalized phone comparison
            const existingChatIndex = prevChats.findIndex(chat => 
                PhoneUtils.matches(chat, phoneNumber)
            )
            
            if (existingChatIndex > -1) {
                // Update existing chat and move to top
                const updatedChats = [...prevChats]
                const existingChat = updatedChats[existingChatIndex]
                
                // Preserve existing chat data while updating new info
                const updatedChat = {
                    ...existingChat,
                    lastMessage: messageContent.length > 40 
                        ? `${messageContent.substring(0, 40)}...` 
                        : messageContent,
                    timestamp: formatDateTime(timestamp),
                    unread: true
                }

                // Remove from current position and add to top
                updatedChats.splice(existingChatIndex, 1)
                return [updatedChat, ...updatedChats]
            }
            
            // If no existing chat found, trigger a full reload to get proper chat ID
            loadChats()
            return prevChats
        })
    }

    // Improve the filter function with null checks
    const filteredChats = chats.filter(chat => {
        if (!chat) return false
        
        const searchTermLower = searchTerm.toLowerCase()
        return (
            (chat.name || '').toLowerCase().includes(searchTermLower) ||
            (chat.phoneNumber || '').toLowerCase().includes(searchTermLower) ||
            ((chat.lastMessage || '').toLowerCase().includes(searchTermLower))
        )
    })

    return (
        <div className="flex flex-col h-full">
            <div className="flex-grow-0">
                {connectionStatus !== 'connected' && (
                    <div className={classNames(
                        'mb-2 px-4 py-2 text-sm rounded flex items-center justify-between',
                        connectionStatus === 'connecting' 
                            ? 'bg-yellow-100 dark:bg-yellow-900 text-yellow-800 dark:text-yellow-200'
                            : 'bg-red-100 dark:bg-red-900 text-red-800 dark:text-red-200'
                    )}>
                        <span>
                            {connectionStatus === 'connecting' 
                                ? 'Connecting to WhatsApp...' 
                                : 'WhatsApp Disconnected'}
                        </span>
                        {connectionStatus === 'disconnected' && (
                            <Button 
                                size="xs" 
                                variant="solid" 
                                className="ml-2"
                                onClick={() => window.location.reload()}
                            >
                                Reconnect
                            </Button>
                        )}
                    </div>
                )}
                <Input 
                    placeholder="Search WhatsApp chats..."
                    className="mb-4"
                    value={searchTerm}
                    onChange={e => setSearchTerm(e.target.value)}
                />
            </div>
            <div className="overflow-y-auto flex-grow">
                {loading ? (
                    <div className="text-center py-4">Loading chats...</div>
                ) : chats.length === 0 ? (
                    <div className="text-center py-4 text-gray-500">
                        {connectionStatus === 'connected' 
                            ? 'No WhatsApp conversations found'
                            : 'Waiting for WhatsApp connection...'}
                    </div>
                ) : (
                    filteredChats.map(chat => (
                        <div 
                            key={chat.id}
                            className={classNames(
                                'flex items-center p-4 cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors duration-200',
                                chat.unread && 'bg-gray-50 dark:bg-gray-700'
                            )}
                            onClick={() => {
                                console.log('ChatList: Selecting chat:', {
                                    rawChat: chat,
                                    selectedData: {
                                        id: chat.id,
                                        name: chat.name,
                                        phoneNumber: chat.phoneNumber,
                                        wa_id: chat.wa_id || chat.phoneNumber
                                    }
                                });
                                onSelectUser({
                                    id: chat.id,
                                    name: chat.name,
                                    phoneNumber: chat.phoneNumber,
                                    wa_id: chat.wa_id || chat.phoneNumber
                                });
                            }}
                        >
                            <Avatar size={45}>{getInitials(chat.name)}</Avatar>
                            <div className="ml-3 rtl:mr-3 flex-grow">
                                <div className="flex items-center justify-between">
                                    <div className="font-semibold text-gray-900 dark:text-gray-100">
                                        {chat.name}
                                    </div>
                                    {chat.timestamp && (
                                        <div className="text-xs text-gray-500 dark:text-gray-400">
                                            {chat.timestamp}
                                        </div>
                                    )}
                                </div>
                                <div className="text-sm mt-1">
                                    <div className="text-gray-500 dark:text-gray-400">
                                        {chat.phoneNumber}
                                    </div>
                                    {chat.lastMessage && (
                                        <div className="text-gray-500 dark:text-gray-400 line-clamp-1">
                                            {chat.lastMessage}
                                        </div>
                                    )}
                                </div>
                            </div>
                            {chat.unread && (
                                <div className="w-2 h-2 rounded-full bg-primary ml-2 rtl:mr-2"></div>
                            )}
                        </div>
                    ))
                )}
            </div>
        </div>
    )
}

export default ChatList
