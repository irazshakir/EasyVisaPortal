import ApiService from '@/services/ApiService'

export interface LeadNote {
    id: number
    lead: number
    note: string
    added_by: number
    created_at: string
    updated_at: string
}

export interface CreateLeadNoteData {
    lead: number
    lead_note: string;
}

export interface UpdateLeadNoteData {
    note: string
}

export const leadNoteApi = {
    getNotesByLead: async (leadId: number) => {
        // Adjust endpoint if your backend uses a different filter/query param
        return ApiService.fetchDataWithAxios<LeadNote[]>({
            url: `/api/v1/lead-notes/?lead=${leadId}`,
            method: 'get'
        })
    },

    getNoteById: async (noteId: number) => {
        return ApiService.fetchDataWithAxios<LeadNote>({
            url: `/api/v1/lead-notes/${noteId}/`,
            method: 'get'
        })
    },

    createNote: async (data: CreateLeadNoteData) => {
        return ApiService.fetchDataWithAxios<LeadNote>({
            url: `/api/v1/lead-notes/`,
            method: 'post',
            data
        })
    },

    updateNote: async (noteId: number, data: UpdateLeadNoteData) => {
        return ApiService.fetchDataWithAxios<LeadNote>({
            url: `/api/v1/lead-notes/${noteId}/`,
            method: 'put',
            data
        })
    },

    deleteNote: async (noteId: number) => {
        return ApiService.fetchDataWithAxios<void>({
            url: `/api/v1/lead-notes/${noteId}/`,
            method: 'delete'
        })
    }
}
