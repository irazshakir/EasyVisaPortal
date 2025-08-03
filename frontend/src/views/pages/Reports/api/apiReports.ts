import ApiService from '@/services/ApiService';

export interface ProductStatusReportParams {
    start_date?: string; // format: YYYY-MM-DD
    end_date?: string;   // format: YYYY-MM-DD
    range?: 'today' | 'week' | 'month' | 'year';
}

export interface ProductStatusReportCell {
    status_id: number;
    status_name: string;
    count: number;
}

export interface ProductStatusReportRow {
    product_id: number;
    product_name: string;
    counts: ProductStatusReportCell[];
}

export interface ProductStatusReportNewLeads {
    product_id: number;
    product_name: string;
    new_leads: number;
}

export interface ProductStatusReportResponse {
    products: { id: number; product_name: string }[];
    statuses: { id: number; status_name: string }[];
    matrix: ProductStatusReportRow[];
    new_leads?: ProductStatusReportNewLeads[];
    start_date: string;
    end_date: string;
}

// User Status Report Types
export interface UserStatusReportParams {
    start_date?: string;
    end_date?: string;
    range?: 'today' | 'week' | 'month' | 'year';
}

export interface UserStatusReportCell {
    status_id: number;
    status_name: string;
    count: number;
}

export interface UserStatusReportRow {
    user_id: number;
    name: string;
    email: string;
    counts: UserStatusReportCell[];
}

export interface UserStatusReportNewLeads {
    user_id: number;
    name: string;
    email: string;
    new_leads: number;
}

export interface UserStatusReportResponse {
    users: { id: number; name: string; email: string }[];
    statuses: { id: number; status_name: string }[];
    matrix: UserStatusReportRow[];
    new_leads?: UserStatusReportNewLeads[];
    start_date: string;
    end_date: string;
}

export const reportsApi = {
    getProductStatusReport: async (params?: ProductStatusReportParams) => {
        const response = await ApiService.fetchDataWithAxios<ProductStatusReportResponse>({
            url: '/api/v1/analytics/product-status/',
            method: 'get',
            params,
        });
        return response;
    },
    getUserStatusReport: async (params?: UserStatusReportParams) => {
        const response = await ApiService.fetchDataWithAxios<UserStatusReportResponse>({
            url: '/api/v1/analytics/user-status/',
            method: 'get',
            params,
        });
        return response;
    },
};
