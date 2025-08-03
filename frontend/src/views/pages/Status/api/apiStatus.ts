import ApiService from '@/services/ApiService'

const getToken = () => {
    const auth = localStorage.getItem('auth')
    if (auth) {
        const parsed = JSON.parse(auth)
        return parsed.access_token
    }
    return ''
}

export interface Status {
    id: number
    status_name: string
    is_active: boolean
    timestamp: string
}

export interface StatusListResponse {
    count: number
    results: Status[]
}

export interface UpdateStatusData {
    status_name: string
    is_active: boolean
}

export const statusApi = {
    getStatuses: async (params?: { page?: number, search?: string, is_active?: boolean }) => {
        const response = await ApiService.fetchDataWithAxios<StatusListResponse>({
            url: '/api/v1/statuses/',
            method: 'get',
            params
        })
        return response
    },

    getStatusById: async (statusId: number) => {
        const response = await ApiService.fetchDataWithAxios<Status>({
            url: `/api/v1/statuses/${statusId}/`,
            method: 'get'
        })
        return response
    },

    createStatus: async (data: UpdateStatusData) => {
        const response = await ApiService.fetchDataWithAxios<Status>({
            url: '/api/v1/statuses/',
            method: 'post',
            data
        })
        return response
    },

    updateStatus: async (statusId: number, data: UpdateStatusData) => {
        const response = await ApiService.fetchDataWithAxios<Status>({
            url: `/api/v1/statuses/${statusId}/`,
            method: 'put',
            data
        })
        return response
    },

    deleteStatus: async (statusId: number) => {
        await ApiService.fetchDataWithAxios({
            url: `/api/v1/statuses/${statusId}/`,
            method: 'delete'
        })
    }
}
