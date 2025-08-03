import { useEffect, useState } from 'react'
import { StorageService } from '@/services/StorageService'

export const useAuth = () => {
    const [isAuthenticated, setIsAuthenticated] = useState(false)

    useEffect(() => {
        const token = StorageService.getAccessToken()
        setIsAuthenticated(!!token)

        // Listen for storage changes
        const handleStorageChange = () => {
            const token = StorageService.getAccessToken()
            setIsAuthenticated(!!token)
        }

        window.addEventListener('storage', handleStorageChange)
        return () => {
            window.removeEventListener('storage', handleStorageChange)
        }
    }, [])

    return {
        isAuthenticated
    }
}

export const getToken = (): string => {
    return StorageService.getAccessToken() || ''
} 