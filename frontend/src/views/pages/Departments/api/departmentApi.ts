import ApiService from '@/services/ApiService'

const getToken = () => {
    const auth = localStorage.getItem('auth')
    if (auth) {
        const parsed = JSON.parse(auth)
        return parsed.access_token
    }
    return ''
}

export interface Department {
    id: number
    department_name: string
    is_active: boolean
    created_at: string
    updated_at: string
}

export interface DepartmentListResponse {
    count: number
    results: Department[]
}

export interface UpdateDepartmentData {
    department_name: string
    is_active: boolean
}

export const departmentApi = {
    getDepartments: async (params?: { page?: number, search?: string, is_active?: boolean }) => {
        const response = await ApiService.fetchDataWithAxios<DepartmentListResponse>({
            url: '/api/v1/departments/',
            method: 'get',
            params
        })
        return response
    },

    getDepartmentById: async (departmentId: number) => {
        const response = await ApiService.fetchDataWithAxios<Department>({
            url: `/api/v1/departments/${departmentId}/`,
            method: 'get'
        })
        return response
    },

    createDepartment: async (data: UpdateDepartmentData) => {
        const response = await ApiService.fetchDataWithAxios<Department>({
            url: '/api/v1/departments/',
            method: 'post',
            data
        })
        return response
    },

    updateDepartment: async (departmentId: number, data: UpdateDepartmentData) => {
        const response = await ApiService.fetchDataWithAxios<Department>({
            url: `/api/v1/departments/${departmentId}/`,
            method: 'put',
            data
        })
        return response
    },

    deleteDepartment: async (departmentId: number) => {
        await ApiService.fetchDataWithAxios({
            url: `/api/v1/departments/${departmentId}/`,
            method: 'delete'
        })
    }
}
