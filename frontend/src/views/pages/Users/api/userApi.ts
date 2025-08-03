import ApiService from '@/services/ApiService'

const getToken = () => {
    const auth = localStorage.getItem('auth')
    if (auth) {
        const parsed = JSON.parse(auth)
        return parsed.access_token
    }
    return ''
}

export interface User {
    id: number
    email: string
    name: string
    phone: string
    role: string
    is_active: boolean
    department_name?: string
    department_id?: number
    manager_id?: number
    team_lead_id?: number
    created_at: string
    updated_at: string
}

export interface Department {
    id: number
    department_name: string
    is_active: boolean
}

export interface UserListResponse {
    count: number
    results: User[]
}

export interface UpdateUserData {
    name: string
    phone: string
    role: 'admin' | 'department_head' | 'manager' | 'team_lead' | 'consultant' | 'support'
    is_active: boolean
    password?: string
    department_id?: number
}

export const userApi = {
    getUsers: async (params?: { page?: number, search?: string, role?: string, department?: number }) => {
        const response = await ApiService.fetchDataWithAxios<UserListResponse>({
            url: '/api/v1/list/',
            method: 'get',
            params
        })
        return response
    },

    getDepartments: async () => {
        const response = await ApiService.fetchDataWithAxios<{ results: Department[] }>({
            url: '/api/v1/departments/',
            method: 'get',
            params: { page_size: 100 } // Get all departments
        })
        return response.results
    },

    getUserById: async (userId: number) => {
        const response = await ApiService.fetchDataWithAxios<User>({
            url: `/api/v1/detail/${userId}/`,
            method: 'get'
        })
        return response
    },

    updateUser: async (userId: number, data: UpdateUserData) => {
        const response = await ApiService.fetchDataWithAxios<User>({
            url: `/api/v1/detail/${userId}/`,
            method: 'put',
            data
        })
        return response
    },

    deleteUser: async (userId: number) => {
        await ApiService.fetchDataWithAxios({
            url: `/api/v1/${userId}/`,
            method: 'delete'
        })
    },

    getUsersByDepartment: async (departmentId: number): Promise<User[]> => {
        return await ApiService.fetchDataWithAxios<User[]>({
            url: `/api/v1/users/by_department/?department_id=${departmentId}`,
            method: 'get'
        });
    },
    
    getUsersByManager: async (managerId: number): Promise<User[]> => {
        return await ApiService.fetchDataWithAxios<User[]>({
            url: `/api/v1/users/by_manager/?manager_id=${managerId}`,
            method: 'get'
        });
    },
    
    getHierarchyView: async (): Promise<User[]> => {
        return await ApiService.fetchDataWithAxios<User[]>({
            url: '/api/v1/users/hierarchy_view/',
            method: 'get'
        });
    }
} 