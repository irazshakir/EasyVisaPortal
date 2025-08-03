import ApiService from '@/services/ApiService'

const getToken = () => {
    const auth = localStorage.getItem('auth')
    if (auth) {
        const parsed = JSON.parse(auth)
        return parsed.access_token
    }
    return ''
}

export interface Lead {
    id: number
    name: string
    email: string | null
    phone: string
    product: number | null
    status: number | null
    assigned_user: number | null
    lead_source: string | null
    is_open: boolean
    sale_at: string | null
    closed_at: string | null
    lost_at: string | null
    followup_date: string | null
    followup_time: string | null
    timestamp: string
    lead_potential?: string
}

export interface LeadListResponse {
    count: number
    results: Lead[]
}

export interface CreateLeadData {
    name: string
    email?: string
    phone: string
    product?: number
    status?: number
    assigned_user?: number
    lead_source?: string
    is_open?: boolean
    sale_at?: string
    closed_at?: string
    lost_at?: string
    followup_date?: string
    followup_time?: string
    lead_potential?: string
}

export interface LeadFilterParams {
    phone?: string;
    email?: string;
    name?: string;
    product?: number;
    status?: number;
    is_open?: boolean;
    followup_date_filter?: string;
    page?: number;
    page_size?: number;
    search?: string;
    lead_potential?: string;
}

export interface PaginatedLeads {
    count: number;
    next: string | null;
    previous: string | null;
    results: Lead[];
}

export interface UpdateLeadData extends CreateLeadData {}

export const leadApi = {
    getLeads: async (params?: { page?: number, search?: string, is_open?: boolean }) => {
        const response = await ApiService.fetchDataWithAxios<LeadListResponse>({
            url: '/api/v1/leads/',
            method: 'get',
            params
        })
        return response
    },

    getLeadById: async (leadId: number) => {
        const response = await ApiService.fetchDataWithAxios<Lead>({
            url: `/api/v1/leads/${leadId}/`,
            method: 'get'
        })
        return response
    },

    createLead: async (data: CreateLeadData) => {
        const response = await ApiService.fetchDataWithAxios<Lead>({
            url: '/api/v1/leads/',
            method: 'post',
            data
        })
        return response
    },

    updateLead: async (leadId: number, data: UpdateLeadData) => {
        const response = await ApiService.fetchDataWithAxios<Lead>({
            url: `/api/v1/leads/${leadId}/`,
            method: 'put',
            data
        })
        return response
    },

    deleteLead: async (leadId: number) => {
        await ApiService.fetchDataWithAxios({
            url: `/api/v1/leads/${leadId}/`,
            method: 'delete'
        })
    },

    filterLeads: async (params: LeadFilterParams): Promise<PaginatedLeads> => {
        const response = await ApiService.fetchDataWithAxios<PaginatedLeads>({
            url: '/api/v1/leads/filter/',
            method: 'get',
            params
        })
        return response
    }
}
