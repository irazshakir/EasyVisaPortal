const environmentConfig = {
    apiBaseUrl: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1',
    leadNotificationWsUrl: import.meta.env.VITE_LEAD_NOTIFICATION_WS_URL || 'ws://127.0.0.1:8001/ws/lead-notifications/',
    isDevelopment: import.meta.env.DEV || false,
}

// Log the configuration in development
if (environmentConfig.isDevelopment) {
    console.log('Environment Config:', {
        ...environmentConfig,
        envVars: {
            VITE_API_BASE_URL: import.meta.env.VITE_API_BASE_URL,
            VITE_LEAD_NOTIFICATION_WS_URL: import.meta.env.VITE_LEAD_NOTIFICATION_WS_URL,
        }
    })
}

export default environmentConfig 