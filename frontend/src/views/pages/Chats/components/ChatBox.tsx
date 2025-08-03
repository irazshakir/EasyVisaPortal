import { useState, useEffect, useRef, useMemo } from 'react'
import { Avatar, Input, Button, Dropdown, Badge, Notification } from '@/components/ui'
import { 
    PiPaperPlaneRightFill, 
    PiDotsThreeVerticalBold,
    PiPhoneBold,
    PiTrashBold,
    PiLockBold,
} from 'react-icons/pi'
import classNames from '@/utils/classNames'
import { chatApi, WhatsAppMessage } from '../api/chatApi'
import toast from '@/components/ui/toast'
import { useWebSocket } from '@/contexts/WebSocketContext'

interface SelectedUser {
    id: string
    name: string
    phoneNumber: string
    wa_id?: string
}

interface ChatBoxProps {
    selectedUser: SelectedUser
}

interface WebSocketMessage {
    type: string;
    message: any;
}

interface MessageCacheType {
    [key: string]: WhatsAppMessage;
}

// Message validation interfaces
interface MessageFingerprint {
    id: string;
    timestamp: string;
    contentHash: string;
}

interface MessageValidator {
    isValidMessage: (message: WhatsAppMessage) => boolean;
    isDuplicate: (messageId: string, timestamp: string, content: string) => boolean;
    isSameContent: (message1: WhatsAppMessage, message2: WhatsAppMessage) => boolean;
    addToProcessed: (message: WhatsAppMessage) => void;
    getMessageFingerprint: (id: string, timestamp: string, content: string) => MessageFingerprint;
}

// Phone number utilities for consistent matching with ChatList
const PhoneUtils = {
    normalize: (phone: string): string => {
        const digits = (phone || '').replace(/\D/g, '')
        return digits.slice(-10)
    },
    
    format: (phone: string): string => {
        const digits = (phone || '').replace(/\D/g, '')
        return digits ? `+${digits}` : ''
    },
    
    matches: (user: SelectedUser, phoneNumber: string): boolean => {
        const normalizedIncoming = PhoneUtils.normalize(phoneNumber)
        const normalizedPhone = PhoneUtils.normalize(user.phoneNumber)
        const normalizedWaId = user.wa_id ? PhoneUtils.normalize(user.wa_id) : ''
        
        // Match by phone number or wa_id
        return normalizedPhone === normalizedIncoming || 
               normalizedWaId === normalizedIncoming
    }
}

// Create message validator helper
const createMessageValidator = (
    processedIds: Set<string>,
    messageCache: MessageCacheType,
    onAddProcessed: (messageId: string) => void
): MessageValidator => {
    // Helper to create a simple hash of message content
    const hashContent = (content: string): string => {
        return content.split('').reduce((acc, char) => {
            const hash = ((acc << 5) - acc) + char.charCodeAt(0);
            return hash & hash;
        }, 0).toString();
    };

    // Create message fingerprint for comparison
    const getMessageFingerprint = (id: string, timestamp: string, content: string): MessageFingerprint => ({
        id,
        timestamp,
        contentHash: hashContent(content)
    });

    return {
        isValidMessage: (message: WhatsAppMessage): boolean => {
            return !!(
                message &&
                message.id &&
                message.content &&
                message.timestamp &&
                message.sender
            );
        },

        isDuplicate: (messageId: string, timestamp: string, content: string): boolean => {
            // Check if ID is already processed
            if (processedIds.has(messageId)) {
                // If message exists in cache, check if content is different
                const existingMessage = messageCache[messageId];
                if (existingMessage) {
                    const existingFingerprint = getMessageFingerprint(
                        existingMessage.id,
                        existingMessage.timestamp,
                        existingMessage.content
                    );
                    const newFingerprint = getMessageFingerprint(messageId, timestamp, content);
                    
                    // Return false if content has changed (not a duplicate, but an update)
                    return existingFingerprint.contentHash === newFingerprint.contentHash;
                }
                return true;
            }
            return false;
        },

        isSameContent: (message1: WhatsAppMessage, message2: WhatsAppMessage): boolean => {
            const fingerprint1 = getMessageFingerprint(
                message1.id,
                message1.timestamp,
                message1.content
            );
            const fingerprint2 = getMessageFingerprint(
                message2.id,
                message2.timestamp,
                message2.content
            );
            return fingerprint1.contentHash === fingerprint2.contentHash;
        },

        addToProcessed: (message: WhatsAppMessage): void => {
            onAddProcessed(message.id);
        },

        getMessageFingerprint
    };
};

const getInitials = (name: string) => {
    const names = name.split(' ')
    return names.map(n => n[0]).join('').toUpperCase()
}

// Binary insertion helper for chronological message ordering
const findInsertionIndex = (messages: WhatsAppMessage[], newMessage: WhatsAppMessage): number => {
    let start = 0
    let end = messages.length - 1
    const newTime = new Date(newMessage.timestamp).getTime()

    while (start <= end) {
        const mid = Math.floor((start + end) / 2)
        const midTime = new Date(messages[mid].timestamp).getTime()

        if (midTime === newTime) {
            return mid
        }
        if (midTime < newTime) {
            start = mid + 1
        } else {
            end = mid - 1
        }
    }
    return start
}

const ChatBox = ({ selectedUser }: ChatBoxProps) => {
    // Message management states
    const [messages, setMessages] = useState<WhatsAppMessage[]>([])
    const [messageCache, setMessageCache] = useState<MessageCacheType>({})
    const [processedMessageIds, setProcessedMessageIds] = useState<Set<string>>(new Set())

    // Create message validator instance
    const messageValidator = useMemo(() => createMessageValidator(
        processedMessageIds,
        messageCache,
        (messageId: string) => setProcessedMessageIds(prev => new Set(prev).add(messageId))
    ), [processedMessageIds, messageCache])

    // Pagination states
    const [currentPage, setCurrentPage] = useState(1)
    const [hasMore, setHasMore] = useState(true)
    const [pageSize] = useState(50)

    // Timestamp tracking
    const [oldestMessageTimestamp, setOldestMessageTimestamp] = useState<string | null>(null)
    const [newestMessageTimestamp, setNewestMessageTimestamp] = useState<string | null>(null)

    // Loading states
    const [isInitialLoading, setIsInitialLoading] = useState(true)
    const [isLoadingMore, setIsLoadingMore] = useState(false)
    const [isSending, setIsSending] = useState(false)

    // Other existing states
    const [newMessage, setNewMessage] = useState('')

    // Refs for infinite scroll
    const messagesEndRef = useRef<HTMLDivElement>(null)
    const loadingRef = useRef<HTMLDivElement>(null)
    const observerRef = useRef<IntersectionObserver | null>(null)

    // Track if we should auto scroll
    const shouldAutoScroll = useRef(true)
    const isNearBottom = useRef(false)

    // Handle scroll position
    const handleScroll = (e: React.UIEvent<HTMLDivElement>) => {
        const element = e.target as HTMLDivElement
        const isBottom = element.scrollHeight - element.scrollTop <= element.clientHeight + 100
        isNearBottom.current = isBottom
        shouldAutoScroll.current = isBottom
    }

    const { lastMessage, connectionStatus } = useWebSocket()

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
    }

    useEffect(() => {
        scrollToBottom()
    }, [messages])

    useEffect(() => {
        if (selectedUser.id) {
            console.log('ChatBox: Selected user changed:', {
                id: selectedUser.id,
                name: selectedUser.name,
                phoneNumber: selectedUser.phoneNumber,
                wa_id: selectedUser.wa_id
            })
            loadMessages()
        }
    }, [selectedUser.id])

    // Log connection status changes
    useEffect(() => {
        console.log('ChatBox: WebSocket connection status:', connectionStatus)
        if (connectionStatus === 'connected') {
            console.log('ChatBox: WebSocket connection established')
        }
    }, [connectionStatus])

    // Handle incoming WebSocket messages
    useEffect(() => {
        if (lastMessage?.type === 'whatsapp.message' && lastMessage.message) {
            try {
                console.log('ChatBox: Received WebSocket message:', lastMessage)
                const message = lastMessage.message
                
                // Extract message details using broadcast format
                const messageId = message.id
                const messageContent = message.content
                const phoneNumber = message.phone_number
                const chatName = message.chat_name
                const timestamp = message.timestamp
                const isFromCustomer = message.is_from_customer

                // Log extracted data for debugging
                console.log('ChatBox: Extracted message details:', {
                    messageId,
                    messageContent,
                    phoneNumber,
                    chatName,
                    timestamp,
                    isFromCustomer
                })

                // Validate message using validator
                const isDuplicate = messageValidator.isDuplicate(messageId, timestamp, messageContent)
                if (isDuplicate) {
                    // Check if message content has changed
                    const existingMessage = messageCache[messageId]
                    if (existingMessage && existingMessage.content !== messageContent) {
                        // Update existing message
                        const updatedMessage: WhatsAppMessage = {
                            ...existingMessage,
                            content: messageContent,
                            timestamp: timestamp
                        }

                        // Update cache
                        setMessageCache(prev => ({
                            ...prev,
                            [messageId]: updatedMessage
                        }))

                        // Update messages array efficiently
                        setMessages(prev => {
                            const messageIndex = prev.findIndex(m => m.id === messageId)
                            if (messageIndex === -1) return prev

                            const newMessages = [...prev]
                            newMessages[messageIndex] = updatedMessage
                            return newMessages
                        })
                    }
                    return
                }

                // Create new message object
                const newMessage: WhatsAppMessage = {
                    id: messageId,
                    content: messageContent,
                    sender: {
                        id: null,
                        name: chatName || selectedUser.name,
                        phone_number: phoneNumber
                    },
                    timestamp: timestamp,
                    is_admin: !isFromCustomer
                }

                // Log new message object for debugging
                console.log('ChatBox: Created new message object:', newMessage)

                // Validate the new message
                if (!messageValidator.isValidMessage(newMessage)) {
                    console.warn('ChatBox: Invalid message received:', newMessage)
                    return
                }

                // Use consistent phone number matching with ChatList
                if (PhoneUtils.matches(selectedUser, phoneNumber)) {
                    console.log('ChatBox: Message matches current chat')
                    
                    // Optimize: Skip if message is older than our oldest message or newer than newest
                    const messageTime = new Date(timestamp).getTime()
                    if (newestMessageTimestamp) {
                        const newestTime = new Date(newestMessageTimestamp).getTime()
                        if (messageTime > newestTime) {
                            setNewestMessageTimestamp(timestamp)
                        }
                    } else {
                        setNewestMessageTimestamp(timestamp)
                    }

                    // Batch state updates for better performance
                    const batchUpdates = () => {
                        // Update message cache
                        setMessageCache(prev => ({
                            ...prev,
                            [messageId]: newMessage
                        }))

                        // Add to processed IDs using validator
                        messageValidator.addToProcessed(newMessage)
                        
                        // Update messages with binary insertion
                        setMessages(prev => {
                            const insertIndex = findInsertionIndex(prev, newMessage)
                            // Use efficient array operations
                            if (insertIndex === prev.length) {
                                return [...prev, newMessage]
                            }
                            if (insertIndex === 0) {
                                return [newMessage, ...prev]
                            }
                            const newMessages = [...prev]
                            newMessages.splice(insertIndex, 0, newMessage)
                            return newMessages
                        })
                    }

                    batchUpdates()
                    console.log('ChatBox: Message added to chat')
                    
                    // Only scroll if we're already near bottom
                    if (isNearBottom.current) {
                        scrollToBottom()
                    }
                } else {
                    console.log('ChatBox: Message does not match current chat', {
                        selectedUser,
                        phoneNumber
                    })
                }
            } catch (error) {
                console.error('ChatBox: Error processing WebSocket message:', error)
            }
        }
    }, [lastMessage, selectedUser, messageCache, processedMessageIds, newestMessageTimestamp, messageValidator])

    // Load messages with pagination
    const loadMessages = async (isLoadingMore = false) => {
        if (isLoadingMore && (!hasMore || isLoadingMore)) return
        
        try {
            const loadingState = isLoadingMore ? setIsLoadingMore : setIsInitialLoading
            loadingState(true)
            
            console.log('ChatBox: Loading messages for:', selectedUser.id, {
                page: currentPage,
                pageSize,
                oldestTimestamp: oldestMessageTimestamp
            })

            const response = await chatApi.getWhatsAppMessages(
                selectedUser.id,
                {
                    page: currentPage,
                    pageSize,
                    before: isLoadingMore && oldestMessageTimestamp ? oldestMessageTimestamp : undefined
                }
            )

            if (response?.data) {
                const newMessages = response.data

                // Update timestamps
                if (newMessages.length > 0) {
                    const timestamps = newMessages.map(m => new Date(m.timestamp).getTime())
                    const oldestNew = new Date(Math.min(...timestamps)).toISOString()
                    const newestNew = new Date(Math.max(...timestamps)).toISOString()

                    if (!oldestMessageTimestamp || oldestNew < oldestMessageTimestamp) {
                        setOldestMessageTimestamp(oldestNew)
                    }
                    if (!newestMessageTimestamp || newestNew > newestMessageTimestamp) {
                        setNewestMessageTimestamp(newestNew)
                    }
                }

                // Cache new messages
                const newCache = { ...messageCache }
                newMessages.forEach(message => {
                    if (!processedMessageIds.has(message.id)) {
                        newCache[message.id] = message
                        setProcessedMessageIds(prev => new Set(prev).add(message.id))
                    }
                })
                setMessageCache(newCache)

                // Update messages array
                setMessages(prevMessages => {
                    const allMessages = isLoadingMore 
                        ? [...prevMessages, ...newMessages]
                        : newMessages

                    // Sort by timestamp
                    return allMessages.sort((a, b) => 
                        new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime()
                    )
                })

                // Update pagination
                setHasMore(newMessages.length === pageSize)
                if (isLoadingMore) {
                    setCurrentPage(prev => prev + 1)
                }
            }
        } catch (error) {
            console.error('ChatBox: Failed to load messages:', error)
            toast.push(
                <Notification type="danger">
                    Failed to load messages
                </Notification>
            )
        } finally {
            const loadingState = isLoadingMore ? setIsLoadingMore : setIsInitialLoading
            loadingState(false)
        }
    }

    // Setup intersection observer for infinite scroll
    useEffect(() => {
        if (!loadingRef.current) return

        const options = {
            root: null,
            rootMargin: '0px',
            threshold: 0.1
        }

        const handleIntersection = (entries: IntersectionObserverEntry[]) => {
            const [entry] = entries
            if (entry.isIntersecting && hasMore && !isLoadingMore && !isInitialLoading) {
                loadMessages(true)
            }
        }

        observerRef.current = new IntersectionObserver(handleIntersection, options)
        observerRef.current.observe(loadingRef.current)

        return () => {
            if (observerRef.current) {
                observerRef.current.disconnect()
            }
        }
    }, [hasMore, isLoadingMore, isInitialLoading])

    // Initial load when user changes
    useEffect(() => {
        if (selectedUser.id) {
            console.log('ChatBox: Initial load for user:', selectedUser)
            setCurrentPage(1)
            setHasMore(true)
            setOldestMessageTimestamp(null)
            setNewestMessageTimestamp(null)
            setMessages([])
            setMessageCache({})
            setProcessedMessageIds(new Set())
            loadMessages()
        }
    }, [selectedUser.id])

    const handleSendMessage = async () => {
        if (!newMessage.trim() || isSending) return

        setIsSending(true)
        try {
            console.log('ChatBox: Sending message:', {
                to: selectedUser.phoneNumber,
                message: newMessage.trim()
            })
            
            const response = await chatApi.sendWhatsAppMessage({
                phone_number: selectedUser.phoneNumber,
                message: newMessage.trim()
            })
            
            if (response?.data) {
                console.log('ChatBox: Message sent successfully:', response.data)
                setMessages(prev => [...prev, response.data])
                setNewMessage('')
                scrollToBottom()
            }
        } catch (error) {
            console.error('ChatBox: Failed to send message:', error)
            toast.push(
                <Notification type="danger">
                    Failed to send message
                </Notification>
            )
        } finally {
            setIsSending(false)
        }
    }

    const handleKeyPress = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault()
            handleSendMessage()
        }
    }

    // Memoize message rendering for better performance
    const renderedMessages = useMemo(() => (
        messages.map(message => (
            <div
                key={message.id}
                className={classNames(
                    'flex items-start gap-3',
                    message.is_admin ? 'flex-row-reverse' : ''
                )}
            >
                <Avatar 
                    size={32} 
                    className={message.is_admin ? 'bg-primary text-white' : 'bg-gray-300'}
                >
                    {message.is_admin ? 'A' : getInitials(selectedUser.name)}
                </Avatar>
                <div
                    className={classNames(
                        'max-w-[70%] rounded-2xl p-3',
                        message.is_admin
                            ? 'bg-primary text-white'
                            : 'bg-gray-100 dark:bg-gray-700'
                    )}
                >
                    {message.content}
                    <div className="text-xs mt-1 opacity-70">
                        {new Date(message.timestamp).toLocaleTimeString()}
                    </div>
                </div>
            </div>
        ))
    ), [messages, selectedUser.name])

    if (!selectedUser) {
        return (
            <div className="flex items-center justify-center h-full text-gray-500">
                Select a conversation to start chatting
            </div>
        )
    }

    const dropdownItems = [
        {
            key: 'delete',
            label: 'Delete Chat',
            icon: <PiTrashBold className="text-lg" />,
        },
        {
            key: 'block',
            label: 'Block User',
            icon: <PiLockBold className="text-lg" />,
            variant: 'danger',
        },
    ]

    return (
        <div className="flex flex-col h-full">
            {/* Chat Header */}
            <div className="flex-shrink-0 flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-600">
                <div className="flex items-center">
                    <Avatar size={40}>{getInitials(selectedUser.name)}</Avatar>
                    <div className="ml-3">
                        <div className="font-semibold">{selectedUser.name}</div>
                        <div className="text-sm text-gray-500">
                            <span className="flex items-center gap-1">
                                <PiPhoneBold className="text-base" />
                                {selectedUser.phoneNumber}
                            </span>
                        </div>
                    </div>
                </div>
                <div className="flex items-center gap-2">
                    {connectionStatus !== 'connected' && (
                        <Badge className="mr-2" innerClass={connectionStatus === 'connecting' ? 'bg-yellow-500' : 'bg-red-500'}>
                            {connectionStatus === 'connecting' ? 'Connecting to WhatsApp...' : 'WhatsApp Disconnected'}
                        </Badge>
                    )}
                    <Dropdown
                        placement="bottom-end"
                        renderTitle={
                            <Button
                                variant="plain"
                                icon={<PiDotsThreeVerticalBold />}
                                shape="circle"
                            />
                        }
                    >
                        {dropdownItems.map((item) => (
                            <Dropdown.Item
                                key={item.key}
                                eventKey={item.key}
                                className={classNames(
                                    'flex items-center gap-2',
                                    item.variant === 'danger' && 'text-red-500'
                                )}
                            >
                                {item.icon}
                                <span>{item.label}</span>
                            </Dropdown.Item>
                        ))}
                    </Dropdown>
                </div>
            </div>

            {/* Messages */}
            <div 
                className="flex-grow overflow-y-auto p-4 space-y-4" 
                style={{ maxHeight: 'calc(100vh - 200px)' }}
                onScroll={handleScroll}
            >
                {/* Loading More Indicator */}
                {hasMore && (
                    <div ref={loadingRef} className="text-center py-2">
                        {isLoadingMore && (
                            <div className="text-gray-500">Loading more messages...</div>
                        )}
                    </div>
                )}

                {/* Messages */}
                {isInitialLoading && messages.length === 0 ? (
                    <div className="text-center">Loading messages...</div>
                ) : messages.length === 0 ? (
                    <div className="text-center text-gray-500">
                        No messages yet. Start the conversation!
                    </div>
                ) : (
                    renderedMessages
                )}
                <div ref={messagesEndRef} />
            </div>

            {/* Message Input */}
            <div className="flex-shrink-0 p-4 border-t border-gray-200 dark:border-gray-600">
                <div className="flex items-center gap-2">
                    <Input
                        value={newMessage}
                        onChange={e => setNewMessage(e.target.value)}
                        onKeyPress={handleKeyPress}
                        placeholder={connectionStatus === 'connected' ? "Type your message..." : "Connecting to WhatsApp..."}
                        className="flex-grow"
                        disabled={isSending || connectionStatus !== 'connected'}
                    />
                    <Button
                        variant="solid"
                        onClick={handleSendMessage}
                        loading={isSending}
                        icon={<PiPaperPlaneRightFill />}
                        disabled={connectionStatus !== 'connected'}
                    >
                        Send
                    </Button>
                </div>
            </div>
        </div>
    )
}

export default ChatBox
