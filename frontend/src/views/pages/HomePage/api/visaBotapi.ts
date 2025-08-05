import ApiService from '@/services/ApiService'
import type { AxiosRequestConfig } from 'axios'

// Types for VisaBot API
export interface ChatRequest {
    session_id?: string
    message: string
    context?: Record<string, any>
}

export interface ChatResponse {
    session_id: string
    message: string
    state: string
    metadata?: Record<string, any>
    timestamp: string
}

export interface SessionStatus {
    session_id: string
    state: string
    progress?: number
    metadata?: Record<string, any>
}

export interface EvaluationSummary {
    session_id: string
    evaluation: Record<string, any>
    recommendations: string[]
    status: string
}

export interface ChatHistory {
    session_id: string
    history: Array<{
        role: 'user' | 'assistant' | 'system'
        content: string
        timestamp: string
        metadata?: Record<string, any>
    }>
}

export interface ActiveSession {
    session_id: string
    created_at: string
    last_activity: string
    state: string
}

class VisaBotApi {
    private readonly baseUrl: string = '/api/v1/chat'

    /**
     * Send a message to the VisaBot and get response
     */
    async sendMessage(request: ChatRequest): Promise<ChatResponse> {
        try {
            const config: AxiosRequestConfig & { skipAuthHeader?: boolean } = {
                url: this.baseUrl,
                method: 'POST',
                data: request,
                skipAuthHeader: true, // No auth required for public chat
                withCredentials: false // Disable credentials for CORS
            }

            const response = await ApiService.fetchDataWithAxios<ChatResponse>(config)
            return response
        } catch (error) {
            console.error('Error sending message to VisaBot:', error)
            throw error
        }
    }

    /**
     * Get current session status and progress
     */
    async getSessionStatus(sessionId: string): Promise<SessionStatus> {
        try {
            const config: AxiosRequestConfig & { skipAuthHeader?: boolean } = {
                url: `${this.baseUrl}/status/${sessionId}`,
                method: 'GET',
                skipAuthHeader: true,
                withCredentials: false
            }

            const response = await ApiService.fetchDataWithAxios<SessionStatus>(config)
            return response
        } catch (error) {
            console.error('Error getting session status:', error)
            throw error
        }
    }

    /**
     * Reset a session to start over
     */
    async resetSession(sessionId: string): Promise<{ message: string }> {
        try {
            const config: AxiosRequestConfig & { skipAuthHeader?: boolean } = {
                url: `${this.baseUrl}/reset/${sessionId}`,
                method: 'POST',
                skipAuthHeader: true,
                withCredentials: false
            }

            const response = await ApiService.fetchDataWithAxios<{ message: string }>(config)
            return response
        } catch (error) {
            console.error('Error resetting session:', error)
            throw error
        }
    }

    /**
     * Get evaluation summary for completed sessions
     */
    async getEvaluationSummary(sessionId: string): Promise<EvaluationSummary> {
        try {
            const config: AxiosRequestConfig & { skipAuthHeader?: boolean } = {
                url: `${this.baseUrl}/evaluation/${sessionId}`,
                method: 'GET',
                skipAuthHeader: true,
                withCredentials: false
            }

            const response = await ApiService.fetchDataWithAxios<EvaluationSummary>(config)
            return response
        } catch (error) {
            console.error('Error getting evaluation summary:', error)
            throw error
        }
    }

    /**
     * Get chat history for a session
     */
    async getChatHistory(sessionId: string): Promise<ChatHistory> {
        try {
            const config: AxiosRequestConfig & { skipAuthHeader?: boolean } = {
                url: `${this.baseUrl}/history/${sessionId}`,
                method: 'GET',
                skipAuthHeader: true,
                withCredentials: false
            }

            const response = await ApiService.fetchDataWithAxios<ChatHistory>(config)
            return response
        } catch (error) {
            console.error('Error getting chat history:', error)
            throw error
        }
    }

    /**
     * List all active sessions
     */
    async listActiveSessions(): Promise<{ sessions: ActiveSession[] }> {
        try {
            const config: AxiosRequestConfig & { skipAuthHeader?: boolean } = {
                url: `${this.baseUrl}/sessions`,
                method: 'GET',
                skipAuthHeader: true,
                withCredentials: false
            }

            const response = await ApiService.fetchDataWithAxios<{ sessions: ActiveSession[] }>(config)
            return response
        } catch (error) {
            console.error('Error listing active sessions:', error)
            throw error
        }
    }

    /**
     * End a chat session
     */
    async endSession(sessionId: string): Promise<{ message: string }> {
        try {
            const config: AxiosRequestConfig & { skipAuthHeader?: boolean } = {
                url: `${this.baseUrl}/session/${sessionId}`,
                method: 'DELETE',
                skipAuthHeader: true,
                withCredentials: false
            }

            const response = await ApiService.fetchDataWithAxios<{ message: string }>(config)
            return response
        } catch (error) {
            console.error('Error ending session:', error)
            throw error
        }
    }
}

// Create and export a singleton instance
const visaBotApi = new VisaBotApi()
export default visaBotApi
