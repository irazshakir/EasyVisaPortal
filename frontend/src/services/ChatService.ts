import ApiService from './ApiService'
import { AxiosRequestConfig } from 'axios'

interface User {
    id: string
    name: string
    email: string
}

export interface IMessage {
    id: string
    message: string
    sender: User | null
    receiver: User | null
    visitor_id: string | null
    user: User | null
    is_bot_message: boolean
    is_read: boolean
    created_at: string
    updated_at: string
}

interface MessageData {
    message: string
    visitor_id?: string | null
    is_bot_message?: boolean
    is_widget?: boolean  // Flag to identify widget requests
}

class ChatService {
    private readonly api: typeof ApiService
    private readonly baseUrl: string = '/api/v1'
    private readonly ADMIN_USER_ID = '1'  // Admin/Support user ID

    constructor() {
        this.api = ApiService
    }

    async getMessages(visitorId?: string) {
        try {
            const params = visitorId ? { visitor_id: visitorId } : {}
            const response = await ApiService.fetchDataWithAxios<{ data: { results: IMessage[] } }>({
                url: '/api/v1/chats/',
                method: 'get',
                params
            })
            return response
        } catch (error) {
            throw error
        }
    }

    async sendMessage(messageData: MessageData) {
        try {
            const formattedData = {
                message: messageData.message,
                visitor_id: messageData.visitor_id,
                is_bot_message: messageData.is_bot_message || false
            }

            // For widget messages, use a different endpoint or config
            const config: any = {
                url: '/api/v1/chats/',
                method: 'post',
                data: formattedData
            }

            // If it's a widget message, don't include auth headers
            if (messageData.is_widget) {
                config.skipAuthHeader = true
            }

            const response = await ApiService.fetchDataWithAxios<IMessage>(config)
            return response
        } catch (error) {
            throw error
        }
    }

    async getConversation(userId: string) {
        // If it's a visitor ID (longer than 10 chars), use the messages endpoint
        if (userId.length > 10) {
            const response = await this.getMessages(userId)
            return response.data.results
        }

        const config: AxiosRequestConfig = {
            method: 'GET',
            url: `${this.baseUrl}/chats/conversation/`,
            params: { user_id: userId }
        }
        return this.api.fetchDataWithAxios<IMessage[]>(config)
    }

    async getUnreadCount() {
        const config: AxiosRequestConfig = {
            method: 'GET',
            url: `${this.baseUrl}/chats/unread_count/`
        }
        return this.api.fetchDataWithAxios<{ unread_count: number }>(config)
    }

    async markAsRead(messageId: string) {
        const config: AxiosRequestConfig = {
            method: 'PATCH',
            url: `${this.baseUrl}/chats/${messageId}/`,
            data: {
                is_read: true
            }
        }
        return this.api.fetchDataWithAxios<IMessage>(config)
    }
}

const chatService = new ChatService()
export default chatService 