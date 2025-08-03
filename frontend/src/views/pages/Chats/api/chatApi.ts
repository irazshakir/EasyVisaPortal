import ApiService from '@/services/ApiService'
import { AxiosResponse } from 'axios'

export interface ChatUser {
    id: string
    wa_id?: string
    name: string
    phoneNumber: string
    lastMessage?: string
    timestamp?: string
    unread?: boolean
}

export interface WhatsAppMessage {
    id: string
    content: string
    sender: {
        id: string | null
        name: string | null
        phone_number: string | null
    }
    timestamp: string
    is_admin: boolean
}

interface ApiResponse<T> {
    status: string
    data: T
}

interface PaginationParams {
    page?: number;
    pageSize?: number;
    before?: string;
}

export const chatApi = {
    // Get all WhatsApp chats
    getWhatsAppChats: async () => {
        const response = await ApiService.fetchDataWithAxios<ApiResponse<ChatUser[]>>({
            url: '/api/v1/wabachat/chats/',
            method: 'get'
        })
        return response
    },

    // Get messages for a specific chat
    getWhatsAppMessages: async (chatId: string, params?: PaginationParams) => {
        const response = await ApiService.fetchDataWithAxios<ApiResponse<WhatsAppMessage[]>>({
            url: `/api/v1/wabachat/messages/${chatId}/`,
            method: 'get',
            params
        })
        return response
    },

    // Send a WhatsApp message
    sendWhatsAppMessage: async (data: { phone_number: string; message: string }) => {
        const response = await ApiService.fetchDataWithAxios<ApiResponse<WhatsAppMessage>>({
            url: '/api/v1/wabachat/send/',
            method: 'post',
            data
        })
        return response
    }
}
