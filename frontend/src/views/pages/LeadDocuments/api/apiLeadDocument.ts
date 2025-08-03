import ApiService from '@/services/ApiService'

export type DocType = 'pdf' | 'image' | 'word' | 'excel' | 'other'

export interface LeadDocument {
    id: number
    lead_doc: string
    lead: number
    added_by: number | null
    doc_type: DocType
    file?: string
    created_at: string
    updated_at: string
}

export interface LeadDocumentListResponse {
    count: number
    results: LeadDocument[]
}

export interface CreateLeadDocumentData {
    lead_doc: string
    lead: number
    doc_type?: DocType
    file?: File | string
}

export interface UpdateLeadDocumentData {
    lead_doc?: string
    doc_type?: DocType
    file?: File | string
}

export const leadDocumentApi = {
    getDocuments: async (params?: { lead?: number; page?: number; search?: string }) => {
        return ApiService.fetchDataWithAxios<LeadDocumentListResponse>({
            url: '/api/v1/lead-documents/',
            method: 'get',
            params
        })
    },

    getDocumentById: async (id: number) => {
        return ApiService.fetchDataWithAxios<LeadDocument>({
            url: `/api/v1/lead-documents/${id}/`,
            method: 'get'
        })
    },

    createDocument: async (data: CreateLeadDocumentData | FormData, config?: any) => {
        return ApiService.fetchDataWithAxios<LeadDocument>({
            url: '/api/v1/lead-documents/',
            method: 'post',
            data,
            ...(config || {})
        })
    },

    updateDocument: async (id: number, data: UpdateLeadDocumentData) => {
        return ApiService.fetchDataWithAxios<LeadDocument>({
            url: `/api/v1/lead-documents/${id}/`,
            method: 'put',
            data
        })
    },

    deleteDocument: async (id: number) => {
        return ApiService.fetchDataWithAxios<void>({
            url: `/api/v1/lead-documents/${id}/`,
            method: 'delete'
        })
    }
}
