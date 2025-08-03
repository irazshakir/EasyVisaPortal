import React, { createContext, useContext, useEffect, useRef, useState } from 'react'
import environmentConfig from '@/configs/environment.config'
import { jwtDecode } from 'jwt-decode'
import { signInApi } from '@/views/auth/SignIn/api/signInApi'

// Define strict message types
type MessageType = 'connection.established' | 'ping' | 'pong' | 'whatsapp.message' | 'lead.assigned'

interface WebSocketMessage {
    type: MessageType
    message?: any
    lead?: any
}

interface WebSocketContextType {
    lastMessage: WebSocketMessage | null
    connectionStatus: 'connecting' | 'connected' | 'disconnected'
    reconnect: () => void
}

const WebSocketContext = createContext<WebSocketContextType>({
    lastMessage: null,
    connectionStatus: 'disconnected',
    reconnect: () => {}
})

export const useWebSocket = () => useContext(WebSocketContext)

function isTokenExpired(token: string): boolean {
    try {
        const decoded: any = jwtDecode(token)
        if (!decoded.exp) return true
        return decoded.exp * 1000 < Date.now()
    } catch {
        return true
    }
}

async function getValidAccessToken(): Promise<string | null> {
    let accessToken = localStorage.getItem('access_token')
    const refreshToken = localStorage.getItem('refresh_token')
    if (!accessToken) return null
    if (!isTokenExpired(accessToken)) return accessToken
    // Try to refresh
    if (!refreshToken) return null
    try {
        const data = await signInApi.refreshToken(refreshToken)
        if (data && data.access) {
            localStorage.setItem('access_token', data.access)
            return data.access
        }
        return null
    } catch {
        return null
    }
}

export const WebSocketProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null)
    const [connectionStatus, setConnectionStatus] = useState<'connecting' | 'connected' | 'disconnected'>('disconnected')
    // Remove ws/chat websocket logic
    // Only keep lead notification websocket logic

    // Lead notification WebSocket refs
    const leadWsRef = useRef<WebSocket | null>(null)
    const leadReconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null)
    const leadPingIntervalRef = useRef<NodeJS.Timeout | null>(null)
    const leadConnectionTimeoutRef = useRef<NodeJS.Timeout | null>(null)

    // Remove wsRef, reconnectTimeoutRef, pingIntervalRef, connectionTimeoutRef, connectWebSocket, and related state/logic
    // Only keep leadWsRef, leadReconnectTimeoutRef, leadPingIntervalRef, leadConnectionTimeoutRef, connectLeadWebSocket, and related logic

    const connectLeadWebSocket = async () => {
        const token = await getValidAccessToken()
        if (!token) {
            setConnectionStatus('disconnected')
            return
        }
        const wsUrlWithToken = `${environmentConfig.leadNotificationWsUrl}?token=${token}`
        try {
            if (leadWsRef.current) leadWsRef.current.close()
            if (leadReconnectTimeoutRef.current) clearTimeout(leadReconnectTimeoutRef.current)
            if (leadPingIntervalRef.current) clearInterval(leadPingIntervalRef.current)
            if (leadConnectionTimeoutRef.current) clearTimeout(leadConnectionTimeoutRef.current)

            const ws = new WebSocket(wsUrlWithToken)

            ws.onopen = () => {
                setConnectionStatus('connecting')
                leadConnectionTimeoutRef.current = setTimeout(() => {
                    if (connectionStatus === 'connecting') ws.close()
                }, 5000)
            }

            ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data)
                    if (data.type === 'lead.assigned') {
                        setLastMessage(data)
                    }
                    if (data.type === 'connection.established') {
                        setConnectionStatus('connected')
                        if (leadConnectionTimeoutRef.current) clearTimeout(leadConnectionTimeoutRef.current)
                    }
                } catch (error) {
                    // Optionally log error
                }
            }

            ws.onclose = (event) => {
                setConnectionStatus('disconnected')
                if (leadPingIntervalRef.current) clearInterval(leadPingIntervalRef.current)
                if (leadConnectionTimeoutRef.current) clearTimeout(leadConnectionTimeoutRef.current)
                if (!event.wasClean) {
                    leadReconnectTimeoutRef.current = setTimeout(connectLeadWebSocket, 5000)
                }
            }

            ws.onerror = (error) => {
                setConnectionStatus('disconnected')
                if (leadPingIntervalRef.current) clearInterval(leadPingIntervalRef.current)
                if (leadConnectionTimeoutRef.current) clearTimeout(leadConnectionTimeoutRef.current)
            }

            leadWsRef.current = ws
        } catch (error) {
            setConnectionStatus('disconnected')
            if (leadPingIntervalRef.current) clearInterval(leadPingIntervalRef.current)
            if (leadConnectionTimeoutRef.current) clearTimeout(leadConnectionTimeoutRef.current)
            leadReconnectTimeoutRef.current = setTimeout(connectLeadWebSocket, 5000)
        }
    }

    useEffect(() => {
        connectLeadWebSocket()
        return () => {
            if (leadWsRef.current) leadWsRef.current.close()
            if (leadReconnectTimeoutRef.current) clearTimeout(leadReconnectTimeoutRef.current)
            if (leadPingIntervalRef.current) clearInterval(leadPingIntervalRef.current)
            if (leadConnectionTimeoutRef.current) clearTimeout(leadConnectionTimeoutRef.current)
        }
    }, [])

    return (
        <WebSocketContext.Provider value={{ 
            lastMessage, 
            connectionStatus,
            reconnect: connectLeadWebSocket 
        }}>
            {children}
        </WebSocketContext.Provider>
    )
} 