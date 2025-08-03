import { signInApi } from '@/views/auth/SignIn/api/signInApi'
import { StorageService } from './StorageService'
import type {
    SignInCredential,
    SignUpCredential,
    SignInResponse,
    SignUpResponse,
} from '@/@types/auth'

// Define interfaces for forgot/reset password
interface ForgotPassword {
    email: string
}

interface ResetPassword {
    token: string
    password: string
    confirmPassword: string
}

interface ForgotPasswordResponse {
    message: string
}

interface ResetPasswordResponse {
    message: string
}

const API_BASE_URL = '/api/v1/users'

export async function apiSignIn(data: SignInCredential) {
    const response = await signInApi.login({
        email: data.email,
        password: data.password,
    })

    // Store tokens and user data
    StorageService.setAccessToken(response.access)
    StorageService.setRefreshToken(response.refresh)
    StorageService.setUserData(response.user)

    return {
        token: response.access,
        user: response.user,
    }
}

export async function apiSignUp(data: SignUpCredential) {
    // Implement sign up logic here
    throw new Error('Sign up not implemented')
}

export async function apiSignOut() {
    StorageService.clearAuthData()
}

export async function apiForgotPassword(data: ForgotPassword) {
    return signInApi.forgotPassword(data)
}

export async function apiResetPassword(data: ResetPassword) {
    return signInApi.resetPassword(data)
}
