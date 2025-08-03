import ApiService from '@/services/ApiService'
import { SignInRequest, SignInResponse } from './signInTypes'

const API_BASE_URL = '/api/v1'

interface ForgotPasswordRequest {
    email: string
}

interface ResetPasswordRequest {
    token: string
    password: string
    confirmPassword: string
}

interface MessageResponse {
    message: string
}

export const signInApi = {
    login: (credentials: SignInRequest) => {
        return ApiService.fetchDataWithAxios<SignInResponse>({
            url: `${API_BASE_URL}/auth/login/`,
            method: 'post',
            data: credentials,
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken(),
            },
        })
    },

    refreshToken: (refresh_token: string) => {
        return ApiService.fetchDataWithAxios<{ access: string }>({
            url: `${API_BASE_URL}/auth/refresh/`,
            method: 'post',
            data: { refresh: refresh_token },
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken(),
            },
        })
    },

    verifyToken: (token: string) => {
        return ApiService.fetchDataWithAxios<{ status: string }>({
            url: `${API_BASE_URL}/auth/verify/`,
            method: 'post',
            data: { token },
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken(),
            },
        })
    },

    forgotPassword: (data: ForgotPasswordRequest) => {
        return ApiService.fetchDataWithAxios<MessageResponse>({
            url: `${API_BASE_URL}/auth/forgot-password/`,
            method: 'post',
            data,
            headers: {
                'X-CSRFToken': getCsrfToken(),
            },
        })
    },

    resetPassword: (data: ResetPasswordRequest) => {
        return ApiService.fetchDataWithAxios<MessageResponse>({
            url: `${API_BASE_URL}/auth/reset-password/`,
            method: 'post',
            data,
            headers: {
                'X-CSRFToken': getCsrfToken(),
            },
        })
    }
}

// Helper function to get CSRF token from cookies
function getCsrfToken(): string {
    const name = 'csrftoken='
    const decodedCookie = decodeURIComponent(document.cookie)
    const cookieArray = decodedCookie.split(';')
    
    for (let cookie of cookieArray) {
        cookie = cookie.trim()
        if (cookie.indexOf(name) === 0) {
            return cookie.substring(name.length, cookie.length)
        }
    }
    return ''
} 