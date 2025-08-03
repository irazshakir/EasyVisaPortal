import { useState } from 'react'
import { Card } from '@/components/ui'
import ChatList from './components/ChatList'
import ChatBox from './components/ChatBox'

interface SelectedUser {
    id: string
    name: string
    phoneNumber: string
    wa_id?: string
}

const Chats = () => {
    const [selectedUser, setSelectedUser] = useState<SelectedUser | undefined>(undefined)

    const handleUserSelect = (user: SelectedUser) => {
        console.log('Chats: Setting selected user:', user)
        setSelectedUser(user)
    }

    return (
        <div className="h-full">
            <Card className="h-full">
                <div className="flex h-full">
                    <div className="w-80 border-r border-gray-200 dark:border-gray-600 h-full">
                        <ChatList onSelectUser={handleUserSelect} />
                    </div>
                    <div className="flex-grow">
                        {selectedUser ? (
                            <ChatBox selectedUser={selectedUser} />
                        ) : (
                            <div className="flex items-center justify-center h-full">
                                <div className="text-center">
                                    <img 
                                        src="/img/others/chat-welcome.png" 
                                        alt="Start chatting" 
                                        className="mx-auto mb-4 max-w-[300px]"
                                    />
                                    <h4>Start Chatting!</h4>
                                    <p className="text-gray-500 mt-2">Pick a Conversation or Begin a New One</p>
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            </Card>
        </div>
    )
}

export default Chats
