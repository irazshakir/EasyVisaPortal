export interface SignInRequest {
    email: string
    password: string
}

export interface UserData {
    id: number
    email: string
    name: string
    phone: string
    role: 'admin' | 'user' | 'client'
    active_status: boolean
    created_at: string
    updated_at: string
}

export interface SignInResponse {
    access: string
    refresh: string
    user: UserData
} 