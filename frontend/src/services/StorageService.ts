import { UserData } from '@/views/auth/SignIn/api/signInTypes'

const StorageKeys = {
    ACCESS_TOKEN: 'access_token',
    REFRESH_TOKEN: 'refresh_token',
    USER_DATA: 'user_data',
} as const

export const StorageService = {
    // Token Management
    getAccessToken: () => {
        return localStorage.getItem(StorageKeys.ACCESS_TOKEN)
    },

    setAccessToken: (token: string) => {
        localStorage.setItem(StorageKeys.ACCESS_TOKEN, token)
    },

    getRefreshToken: () => {
        return localStorage.getItem(StorageKeys.REFRESH_TOKEN)
    },

    setRefreshToken: (token: string) => {
        localStorage.setItem(StorageKeys.REFRESH_TOKEN, token)
    },

    // User Data Management
    getUserData: (): UserData | null => {
        const data = localStorage.getItem(StorageKeys.USER_DATA)
        return data ? JSON.parse(data) : null
    },

    setUserData: (userData: UserData) => {
        localStorage.setItem(StorageKeys.USER_DATA, JSON.stringify(userData))
    },

    // Clear all auth related data
    clearAuthData: () => {
        localStorage.removeItem(StorageKeys.ACCESS_TOKEN)
        localStorage.removeItem(StorageKeys.REFRESH_TOKEN)
        localStorage.removeItem(StorageKeys.USER_DATA)
    },

    // Check if user is authenticated
    isAuthenticated: () => {
        return !!localStorage.getItem(StorageKeys.ACCESS_TOKEN)
    }
} 