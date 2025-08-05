import visaBotApi, { 
    ChatRequest, 
    ChatResponse, 
    SessionStatus, 
    EvaluationSummary,
    ChatHistory 
} from '@/views/pages/HomePage/api/visaBotapi'

/**
 * VisaBot Service - Handles all VisaBot related operations
 * This service provides a clean interface for the VisaBot functionality
 */
class VisaBotService {
    private currentSessionId: string | null = null

    /**
     * Send a message to the VisaBot
     */
    async sendMessage(message: string, context?: Record<string, any>): Promise<ChatResponse> {
        try {
            const request: ChatRequest = {
                session_id: this.currentSessionId,
                message,
                context
            }

            const response = await visaBotApi.sendMessage(request)
            
            // Update session ID if it's a new session
            if (response.session_id && !this.currentSessionId) {
                this.currentSessionId = response.session_id
            }

            return response
        } catch (error) {
            console.error('VisaBotService: Error sending message:', error)
            throw error
        }
    }

    /**
     * Get current session status
     */
    async getSessionStatus(): Promise<SessionStatus | null> {
        if (!this.currentSessionId) {
            return null
        }

        try {
            return await visaBotApi.getSessionStatus(this.currentSessionId)
        } catch (error) {
            console.error('VisaBotService: Error getting session status:', error)
            throw error
        }
    }

    /**
     * Reset the current session
     */
    async resetSession(): Promise<void> {
        if (!this.currentSessionId) {
            return
        }

        try {
            await visaBotApi.resetSession(this.currentSessionId)
            this.currentSessionId = null
        } catch (error) {
            console.error('VisaBotService: Error resetting session:', error)
            throw error
        }
    }

    /**
     * Get evaluation summary for the current session
     */
    async getEvaluationSummary(): Promise<EvaluationSummary | null> {
        if (!this.currentSessionId) {
            return null
        }

        try {
            return await visaBotApi.getEvaluationSummary(this.currentSessionId)
        } catch (error) {
            console.error('VisaBotService: Error getting evaluation summary:', error)
            throw error
        }
    }

    /**
     * Get chat history for the current session
     */
    async getChatHistory(): Promise<ChatHistory | null> {
        if (!this.currentSessionId) {
            return null
        }

        try {
            return await visaBotApi.getChatHistory(this.currentSessionId)
        } catch (error) {
            console.error('VisaBotService: Error getting chat history:', error)
            throw error
        }
    }

    /**
     * End the current session
     */
    async endSession(): Promise<void> {
        if (!this.currentSessionId) {
            return
        }

        try {
            await visaBotApi.endSession(this.currentSessionId)
            this.currentSessionId = null
        } catch (error) {
            console.error('VisaBotService: Error ending session:', error)
            throw error
        }
    }

    /**
     * Get the current session ID
     */
    getCurrentSessionId(): string | null {
        return this.currentSessionId
    }

    /**
     * Set the current session ID (useful for restoring sessions)
     */
    setCurrentSessionId(sessionId: string): void {
        this.currentSessionId = sessionId
    }

    /**
     * Check if there's an active session
     */
    hasActiveSession(): boolean {
        return this.currentSessionId !== null
    }

    /**
     * Clear the current session (without calling the API)
     */
    clearSession(): void {
        this.currentSessionId = null
    }
}

// Create and export a singleton instance
const visaBotService = new VisaBotService()
export default visaBotService 