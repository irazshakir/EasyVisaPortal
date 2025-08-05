import axios from 'axios'
import { StorageService } from '../StorageService'
import { signInApi } from '@/views/auth/SignIn/api/signInApi'
import type { AxiosError, AxiosRequestConfig, InternalAxiosRequestConfig } from 'axios'

// Get the API URL from environment variables
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const axiosInstance = axios.create({
    baseURL: API_URL,
    timeout: 30000,
    headers: {
        'Content-Type': 'application/json',
    },
    withCredentials: false, // Disable credentials for VisaBot API
})

// Request interceptor for adding auth token
axiosInstance.interceptors.request.use(
    (config: InternalAxiosRequestConfig) => {
        const token = StorageService.getAccessToken()
        if (token) {
            config.headers.Authorization = `Bearer ${token}`
        }
        return config
    },
    (error: AxiosError) => {
        return Promise.reject(error)
    }
)

// Response interceptor for handling token refresh
axiosInstance.interceptors.response.use(
    (response) => response,
    async (error: AxiosError) => {
        const originalRequest = error.config as AxiosRequestConfig & { _retry?: boolean }
        
        if (error.response?.status === 401 && !originalRequest._retry) {
            originalRequest._retry = true
            
            try {
                const refreshToken = StorageService.getRefreshToken()
                if (!refreshToken) {
                    throw new Error('No refresh token available')
                }

                const response = await signInApi.refreshToken(refreshToken)
                const { access } = response

                StorageService.setAccessToken(access)
                
                // Retry the original request with new token
                if (originalRequest.headers) {
                    originalRequest.headers.Authorization = `Bearer ${access}`
                }
                return axios(originalRequest)
            } catch (refreshError) {
                StorageService.clearAuthData()
                window.location.href = '/sign-in'
                return Promise.reject(refreshError)
            }
        }
        
        return Promise.reject(error)
    }
)

export default axiosInstance
